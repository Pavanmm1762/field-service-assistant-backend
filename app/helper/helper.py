RAG_KEYWORDS = {
    "install",
    "installation",
    "configure",
    "configuration",
    "setup",
    "manual",
    "troubleshoot",
    "troubleshooting",
    "reset",
    "repair",
    "replace",
    "error",
    "fault",
    "alarm",
    "led",
    "indicator",
    "diagnostic",
    "maintenance",
}   

def should_use_rag(
    message: str,
) -> bool:

    text = message.lower()

    return any(
        keyword in text
        for keyword in RAG_KEYWORDS
    )