import asyncio
from datetime import datetime

from winhye_common.utils.sms import Sample


def test_oss_a(phone_numbers, sign_name, template_code, template_param):
    # 再发送
    a = datetime.now()
    Sample.send_sms(phone_numbers, sign_name, template_code, template_param)
    b = datetime.now()
    print(b - a)


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    test_oss_a(
        '17737263251',
        "北京云汉通航科技有限公司",
        "SMS_223060267",
        '{"code":"66"}'
    )
    # asyncio.run(main('17737263251',
    #                  "北京云汉通航科技有限公司",
    #                  "SMS_223060267",
    #                  '{"code":"55"}'))
