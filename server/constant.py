# Communication protocol
types = [
    'WHO_YOU_ARE',
    'AUTH_USER',            # 0
    'AUTH_SUCC_USER',
    'AUTH_FAIL_USER',
    'AUTH_DEVICE',
    'AUTH_SUCC_DEVICE',
    'UPDATE_DEVICE',
    'UPDATE_DEVICE_SUCC',
    'ACT_SYNC',
    'SYNC_DEVICE',          # 8

    'ACT_ACQUIRE',
    'ACT_SYNC_SW_BTN',
    'ACT_SYNC_SW_BTN_SUCC',
    'INIT_FILE_UPLOAD',
    'INIT_FILE_UPLOAD_SUCC',    # 13
    'ACQUIRE_FAIL',
    'ACQUIRE_SUCC',
    'ACQUIRE_DEVICE_FOR_EXP',
    'ACQUIRE_DEVICE_SUCC_EXP',
    'ACQUIRE_DEVICE_FOR_TEST',  # 18
    'ACQUIRE_DEVICE_SUCC_TEST',

    'ACT_RELEASE',

    'REQ_SEG',
    'REQ_SEG_SUCC',
    'REQ_LED',
    'REQ_LED_SUCC', # 24
    'REQ_READ_DATA',
    'REQ_READ_DATA_SUCC',

    'OP_PROGRAM',
    'OP_PROGRAM_SUCC',

    'OP_SW_OPEN',
    'OP_SW_CLOSE',
    'OP_SW_OPEN_DEVICE',
    'OP_SW_CLOSE_DEVICE',
    'OP_SW_CHANGED',

    'OP_BTN_PRESS',
    'OP_BTN_RELEASE',
    'OP_BTN_PRESS_DEVICE',
    'OP_BTN_RELEASE_DEVICE',
    'OP_BTN_CHANGED',

    'OP_PS2_SEND',
    'OP_PS2_SEND_SUCC',

    'AUTH_RABBIT',
    'AUTH_RABBIT_SUCC',
    'AUTH_RABBIT_FAIL',

    'AUTH_RABBIT',
    'AUTH_RABBIT_SUCC',
    'AUTH_RABBIT_FAIL',
    'TEST_PROGRAM',
    'TEST_PROGRAM_SUCC',
    'TEST_PROGRAM_FAIL',
    'TEST_READ_RESULT',
    'TEST_READ_RESULT_SUCC',
]

for i, type_ in enumerate(types):
    exec('{} = {}'.format(type_, i))

SYS_DELAY = 100000000
# SYS_DELAY = 10
UPDATE_TIME = 3  # devices状态更新的周期，单位秒