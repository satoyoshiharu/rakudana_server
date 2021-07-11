INF_OK = 0
INF_RESET = 1
INF_NOT_HEAR_WELL = 2
INF_NO_MATCHING_NAME  = 3
INF_NO_TARGET_WORDS = 4
INF_MULTIPLE_MATCH = 5

SUCCESS = 0
ERR_EXCEPTION = 1
ERR_TIMEOUT = 2
ERR_TYPEERROR = 3

INTENT_OTHERS = 0
INTENT_HELP = INTENT_OTHERS + 1
INTENT_YES = INTENT_HELP + 1
INTENT_NO = INTENT_YES + 1
INTENT_CANCEL = INTENT_NO + 1
INTENT_RETRY = INTENT_CANCEL + 1
INTENT_TEL = INTENT_RETRY + 1
INTENT_SEND_LINE_MESSAGE = INTENT_TEL + 1
INTENT_SEND_SHORT_MESSAGE = INTENT_SEND_LINE_MESSAGE + 1
INTENT_MAX = INTENT_SEND_SHORT_MESSAGE

# display string
intents = {
    INTENT_OTHERS:"others",
    INTENT_HELP:"help",
    INTENT_YES:"yes",
    INTENT_NO: "no",
    INTENT_CANCEL: "cancel",
    INTENT_RETRY: "retry",
    INTENT_TEL:"tel",
    INTENT_SEND_LINE_MESSAGE:"send_line_message",
    INTENT_SEND_SHORT_MESSAGE: "send_short_message",
}