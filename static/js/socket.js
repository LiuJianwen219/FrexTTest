ifLocal = true
ifDebugex = true

const types = [
    'WHO_YOU_ARE',
    'AUTH_USER',
    'AUTH_SUCC_USER',
    'AUTH_FAIL_USER',
    'AUTH_DEVICE',
    'AUTH_SUCC_DEVICE',
    'UPDATE_DEVICE',
    'UPDATE_DEVICE_SUCC',
    'ACT_SYNC',
    'SYNC_DEVICE',

    'ACT_ACQUIRE',
    'ACT_SYNC_SW_BTN',
    'ACT_SYNC_SW_BTN_SUCC',
    'INIT_FILE_UPLOAD',
    'INIT_FILE_UPLOAD_SUCC',
    'ACQUIRE_FAIL',
    'ACQUIRE_SUCC',
    'ACQUIRE_DEVICE_FOR_EXP',
    'ACQUIRE_DEVICE_SUCC_EXP',
    'ACQUIRE_DEVICE_FOR_TEST',
    'ACQUIRE_DEVICE_SUCC_TEST',

    'ACT_RELEASE',

    'REQ_SEG',
    'REQ_SEG_SUCC',
    'REQ_LED',
    'REQ_LED_SUCC',
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

    'AUTH_ADMIN',
    'AUTH_ADMIN_SUCC',
    'AUTH_ADMIN_FAIL',
    'ACT_SYNC_DETAIL',
    'ACT_SYNC_DETAIL_SUCC',
]

const typeList = {}
types.forEach((val, index) => {
    /*
     * note that this statement will be executed
     * in ES5 environment.
     */
    typeList[val] = index
})

// make this more appropriate
const mLocation = { host: 'exotic.zjusig.com' }
const lLocation = { host: '47.96.95.218:30040' }
let myLocation = null
if ( ifLocal ) {
	myLocation = lLocation
} else {
	myLocation = mLocation
}

let socketMy = null
function start_web_socket() {
    socketMy = new WebSocket(`ws://${myLocation.host}`)
    socketMy.onopen = (event) => {
        sleepFor(2000);
		remote.sync() // without this maybe connect failed
	}
    socketMy.onclose = (event) => {
		if (ifDebugex) console.log('关闭设备')
	}
	socketMy.onerror = (event) =>{
		if (ifDebugex) console.log("Error: " + event.name + " " + event.number)
	}
    socketMy.onmessage = (event) => {
        if (ifDebugex) console.log('recv message :',event.data);
        const data = JSON.parse(event.data);
        switch (data.type){
            case typeList.WHO_YOU_ARE:{
				remote.auth_admin();
				break;
			}
            case typeList.AUTH_ADMIN_SUCC:{
                if (ifDebugex) console.log("auth admin success");
                break;
            }
            case typeList.AUTH_ADMIN_FAIL:{
                if (ifDebugex) console.log("auth admin failed");
                break;
            }
            case typeList.ACT_SYNC_DETAIL_SUCC:{
                if (ifDebugex) console.log(data.content.deviceDetail);
                syncDeviceDetail2(data.content.deviceDetail);
                break;
            }
        }
    }
}

const remote = {
	auth_admin: () => {
		send({
			type: typeList.AUTH_ADMIN
		})
	},
	sync_device_detail: () => {
		send({
			type: typeList.ACT_SYNC_DETAIL,
		})
	},
    sync: () => {
		send({
			type: typeList.ACT_SYNC,
			using: "EXPERIMENT",
		})
	},
}

function send(obj){
	if (ifDebugex) console.log(obj)
	if (socketMy.readyState === WebSocket.OPEN) {
		socketMy.send(JSON.stringify(obj))
	} else {
		console.log('无法连接设备，请重新获取')
	}
}

function sleepFor(sleepDuration){
    let now = new Date().getTime();
    while(new Date().getTime() < now + sleepDuration){
        /* Do nothing */
    }
}



