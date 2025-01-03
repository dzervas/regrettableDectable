import asyncio
from MailProtocol import MailProtocol
import serial_asyncio
from ppApi import PpApi, ApiPpUle


async def main():
    port = "/dev/ttyUSB0"
    baudrate = 115200

    print(f"Connecting to {port} at {baudrate} baud...")
    loop = asyncio.get_running_loop()
    transport, protocol = await serial_asyncio.create_serial_connection(
        loop, lambda: MailProtocol(), port, baudrate
    )
    protocol.transport = transport

    asyncio.create_task(protocol.poll_timer())

    await asyncio.sleep(2)

    print("Sending 'API_FP_GET_FW_VERSION' request command...")

    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x4002,
        params=[],
    )
    print("Sending 'API_FP_MM_GET_ID_REQ' request command...")

    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x4004,
        params=[],
    )
    print("Sending 'API_FP_MM_GET_ACCESS_CODE_REQ' request command...")

    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x400A,
        params=[],
    )
    print("Sending 'API_HAL_LED_REQ' request command...")

    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x5902,
        params=[0x02, 0x03, 0x01, 0x2C, 0x01, 0x00, 0x2C, 0x01, 0x02, 0x0A, 0x00],
    )

    await asyncio.sleep(2)

    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x5802,  # API_IMAGE_ACTIVATE_REQ
        params=[
            0xFF,
            0,
        ],  # Image index (just wake up), Activate co-located applications
    )
    await asyncio.sleep(2)

    # Image list (got with API_IMAGE_INFO_REQ):
    # 0: CVM441FPNATALIEV3_FPCVM_V1183_B0000
    # 1: CVM441PPNATALIEV3_FPCVM_V1183_B0000

    print("Activating FP image...")
    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x5802,  # API_IMAGE_ACTIVATE_REQ
        params=[0, 0],  # Image index, Activate co-located applications
    )
    await asyncio.sleep(2)

    print("Defaulting FP settings...")
    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x4FFE,  # API_PROD_TEST_REQ
        params=[
            0x02,
            0x01,  # PT_CMD_NVS_DEFAULT
            0x01,
            0x00,  # Parameter len
            0x00,  # Do not factory reset adjusted parameters
        ],
    )
    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x5802,  # API_IMAGE_ACTIVATE_REQ
        params=[
            0xFF,
            0,
        ],  # Image index (just wake up), Activate co-located applications
    )
    await asyncio.sleep(2)
    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x5802,  # API_IMAGE_ACTIVATE_REQ
        params=[
            0xFF,
            0,
        ],  # Image index (just wake up), Activate co-located applications
    )
    await asyncio.sleep(2)

    print("Sending 'API_PROD_TEST_REQ' request command...")
    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x4FFE,  # API_PROD_TEST_REQ
        params=[
            0x00,
            0x02,  # SET_DECT_MODE
            0x01,  # Parameter len
            0x00,
            0x00,  # EU
        ],
    )

    print("==== Entering registration mode ====")
    protocol.send_command(
        program_id=0,
        task_id=1,
        primitive=0x4105,  # API_FP_MM_SET_REGISTRATION_MODE_REQ
        params=[
            2,  # Enable registration until a handset is registered
            1,  # DeleteLastHandset (if max handsets reached)
        ],
    )

    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated.")
