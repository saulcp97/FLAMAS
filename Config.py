# Configuración para el sistema.


xmpp_server = "gtirouter.dsic.upv.es"
xmpp_server = "localhost"

DEFAULT_TIMER = 20

web_port = 3000
url = "localhost"
jid_domain = "@" + xmpp_server

# FSM name states Central Federado
SETUP_STATE_CFDL = "SETUP_STATE"
STOP_STATE_CFDL = "STOP_STATE"
SEND_STATE_CFDL = "SEND_STATE"

# Net Configuration Path File
path_csv = 'Network_Structures/Connection_1.csv'

# Data-Set Path
data_set_path = "../data"

CONSENSUS_LOGGER = "CONSENSUS_LOGGER"
MESSAGE_LOGGER = "MESSAGE_LOGGER"


#   Network Structures (8 miembros)
# 4 coalitions 1~3 members each coalition
COALITION_PROBABILITY = 0.75

SERVER_NAME = "scp_Main_Node"

AGENT_NAMES = ["scp_0", "scp_1", "scp_2", "scp_3", "scp_4", "scp_5", "scp_6", "scp_7"]
EPOCH_NUM = 120

# Export the logs and clean log directories
export_logs_root_path = "../experiment_logs/"
export_logs_folder_prefix = "exp"
export_logs_at_end_of_execution = False
export_logs_append_to_last_log_folder_instead_of_create = True  # True: Requires manually creating the folder after a experiment batch to avoid the mixing
logs_root_folder = "Logs"
logs_folders = [
    "Epsilon Logs",
    "Message Logs",
    "Training Logs",
    "Training Time Logs",
    "Weight Logs",
]

# LOGGERS
CONSENSUS_LOGGER = "CONSENSUS_LOGGER"
MESSAGE_LOGGER = "MESSAGE_LOGGER"
WEIGHT_LOGGER = "WEIGHT_LOGGER"
TRAINING_LOGGER = "TRAINING_LOGGER"
EPSILON_LOGGER = "EPSILON_LOGGER"
TRAINING_TIME_LOGGER = "TRAINING_TIME_LOGGER"