from kavenegar import *


def send_otp_code(phone_number, code):
    try:
        api = KavenegarAPI('5030346545434D6454556B597334556762702F504A6C634E775665674C792B73546C683775786345444C453D', )
        params = {
            'sender': '10008663',
            'receptor': phone_number,
            'message': f'Your Verify Code: {code}'
        }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)
