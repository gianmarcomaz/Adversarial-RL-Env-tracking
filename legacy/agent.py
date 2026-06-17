from dotenv import load_dotenv

load_dotenv()

import inspect
import json
import os


MODEL = "openai/gpt-oss-120b:free"
MAX_STEPS = 15


# Convert a Python default value into a small JSON schema hint.
def schema_for_default(default):
    if isinstance(default, bool):
        return {"type": "boolean"}
    if isinstance(default, int):
        return {"type": "integer"}
    if isinstance(default, (float, complex)):
        return {"type": "number"}
    return {"type": "string"}


# Build one OpenAI tool schema from a bound service method.
def build_tool_schema(service_name, method_name, method):
    signature = inspect.signature(method)
    properties = {}
    required = []
    allows_extra_fields = False

    for name, parameter in signature.parameters.items():
        if parameter.kind == inspect.Parameter.VAR_KEYWORD:
            allows_extra_fields = True
            continue
        properties[name] = schema_for_default(parameter.default)
        if parameter.default is inspect.Parameter.empty:
            required.append(name)

    parameters = {"type": "object", "properties": properties, "required": required}
    if allows_extra_fields:
        parameters["additionalProperties"] = True

    return {
        "type": "function",
        "function": {
            "name": f"{service_name}_{method_name}",
            "description": f"Call {service_name}.{method_name}.",
            "parameters": parameters,
        },
    }


# Collect public service methods and expose them as callable tools.
def build_tools(slack, tasks):
    services = {"slack": slack, "tasks": tasks}
    tools = []
    handlers = {}

    for service_name, service in services.items():
        for method_name in dir(service):
            if method_name.startswith("_"):
                continue
            method = getattr(service, method_name)
            if callable(method):
                tool_name = f"{service_name}_{method_name}"
                tools.append(build_tool_schema(service_name, method_name, method))
                handlers[tool_name] = method

    return tools, handlers


# Safely turn a service result into JSON text for the LLM.
def result_to_text(result):
    return json.dumps(result, indent=2, default=str)


# Convert an SDK tool call into the plain dict format expected in message history.
def tool_call_to_message(tool_call):
    return {
        "id": tool_call.id,
        "type": "function",
        "function": {
            "name": tool_call.function.name,
            "arguments": tool_call.function.arguments,
        },
    }


# Match a noisy model tool name to a known handler when possible.
def clean_tool_name(name, handlers):
    if name in handlers:
        return name
    for handler_name in sorted(handlers, key=len, reverse=True):
        if name.startswith(handler_name):
            return handler_name
    return name


# Parse tool arguments without letting bad JSON crash the run.
def parse_tool_arguments(text):
    try:
        return json.loads(text or "{}")
    except json.JSONDecodeError:
        return {}


# Run a minimal offline trajectory when no OpenRouter key is configured.
def run_offline_placeholder(instruction):
    return [
        {
            "role": "user",
            "content": instruction,
            "tool_calls": [],
            "tool_results": [],
        },
        {
            "role": "assistant",
            "content": "OPENROUTER_API_KEY is not set, so no LLM call was made.",
            "tool_calls": [],
            "tool_results": [],
        },
    ]


# Execute an instruction with OpenRouter tool calling until the model finishes.
def run_agent(instruction, slack, tasks, model=MODEL):
    if not os.environ.get("OPENROUTER_API_KEY"):
        return run_offline_placeholder(instruction)

    from openai import OpenAI

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
    tools, handlers = build_tools(slack, tasks)
    messages = [{"role": "user", "content": instruction}]
    trajectory = [{"role": "user", "content": instruction, "tool_calls": [], "tool_results": []}]

    for _ in range(MAX_STEPS):
        response = client.chat.completions.create(model=model, messages=messages, tools=tools)
        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls or []
        content = assistant_message.content or ""
        messages.append(
            {
                "role": "assistant",
                "content": content,
                "tool_calls": [tool_call_to_message(tool_call) for tool_call in tool_calls],
            }
        )

        step = {"role": "assistant", "content": content, "tool_calls": [], "tool_results": []}
        for tool_call in tool_calls:
            raw_name = tool_call.function.name
            name = clean_tool_name(raw_name, handlers)
            arguments = parse_tool_arguments(tool_call.function.arguments)

            # Return tool errors to the model instead of raising.
            if name not in handlers:
                result = {"error": f"Unknown tool: {raw_name}"}
            else:
                try:
                    result = handlers[name](**arguments)
                except TypeError as error:
                    result = {"error": str(error)}

            result_text = result_to_text(result)
            step["tool_calls"].append({"name": name, "arguments": arguments})
            step["tool_results"].append({"name": name, "result": result})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result_text})

        trajectory.append(step)
        if not tool_calls:
            break

    return trajectory
