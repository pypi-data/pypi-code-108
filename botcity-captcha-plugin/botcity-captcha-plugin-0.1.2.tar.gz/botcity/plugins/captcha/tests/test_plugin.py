import os

from botcity.plugins.captcha import BotAntiCaptchaPlugin, BotDeathByCaptchaPlugin

bfs = ('03AGdBq26uIeGEu9vxEl8xBEFMUCuoUIOuF-icEED9njuQYtuurWv0tdRvFu6-zdEgjFlAGKGQO7f8bZl2X5BosigbhQUv6NLgpG1L'
       'rSUaRe5PRLjZ53ezrqnZLnF_BL7kDdjkCB7xs1fdeCrmODefnM-fn1KUvbkerjsQXrkqxKly6Fz2o9CQPSf4DLA-Luz_Z9L41vwWDQ'
       '5G3mRYnFXWQhvvpqsZTfBGZDM9sshwq4rfyEmGMYNI0A6QrEHrU2eneuUJ8PU3K2FZYQhVlRWfiu6OwdtXOj_u2iOVGzysfHtYMc5q'
       '_zVRfRQkuvFewbpr2yd53bUWuYWREy5kAel1XyfLDrgb7ofvQOz1MvP_Z_7lEfUBPRo9RkHhUnUgRHF0Uv3ELi4KVo9QzE0sWjZWZg'
       'oJ76ik2W600e3awhughRpT-SgDHQYW2r3z3uum3jA7H0wizbDqIjz-3F5le8rqyJ_n1giLT_NCvvVcziNB5RM_KWDcqinKOWUgkXvK'
       'OzBjaWN8Qlxcapby7fFrsV85PsGOZKWOTPqwoDrVfL_Oiq1B5qutqSgKCO3ZtiQo0j_1dnA1O0-hOSECY5wX5KMwwK2rbz1H8ihyWz'
       'ksurXEMMCG1-_gK4R9fOr2xgR9lMr7VYur4HarEMM0SlHecT_NNGGkuLOFQZy42U714nsulVd3BHuGE1L4HXxH54YgxN_ZRbqBoWMs'
       'EfpZqQefDAvVUDKOVZBURt6E0OCLT1o23dAVBtRPl6DeIrgsUJIFG_By0QxJnHW4wcdP-UdZiXPoGyVSaZ4EKeKqfgrNH2JJUoMYLJ'
       'JKk-yYSDDSwdSTK-Jdlj_iEhFFJaDbrqXBYgshPXmxIqK9X6g4GcgX8UwJbzNv0jMpyKLnTpeN9Jh3pZOlCLhUg3XvqsijYVqMocou'
       'a4vhcRwB6oPv0ATlUsG0su2qqIEYR9nTtjxzjYq0ayqC23_ypUl3fEAmb30EyMHB7kZ-UwfRQ108H92msZc_N7rdozjYHE-CSlKgNx'
       '7SMS89XIEmo06NJrr_JM2428xTIshEi_uyOkdW96yjUckSD3Mxqyeylu5xXbXpb283PX2vhkkLdkQt1Cq1GWqv5A3t0YE-Q2a0PwXg'
       'IUR2OVns-GJTTo605WnNom43qD57NH7_veOwWJy9deWV-ydu_ScGLFUI289jrgAgMOgp0wuCMyYRzurIopG0t8FrlcHb_f0OjBEf9o'
       'u3ZHb7VtbrFbePdILtAJQ_7lqHPgMsnYdzKda_J266-jp7B27_LrOYxaxLK-85wReiuXW8tU7z-K0Kder5ImFo_IrWEp1iunOwVouh'
       'gqQK9LNF46EnwZFAS9VUY41fFwgHemI0x8eLmeNa4P4K8XMe1eYD2kgSQ-ho1IbkspDBD05p_yKskW-_rTUEZLfMsD5xKAAT')


cur_dir = os.path.abspath(os.path.dirname(__file__))


def test_anticaptcha() -> None:
    # AntiCaptcha - Text
    anti_captcha = BotAntiCaptchaPlugin(os.getenv("ANTICAPTCHA_KEY"))
    assert anti_captcha.solve_text(os.path.join(cur_dir, "captcha_ms.jpeg")) == '56nn2'

    # # AntiCaptcha - Re - Revisit this one later.
    # url = 'https://www.google.com/recaptcha/api2/demo'
    # site_key = '6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-'
    # assert anti_captcha.solve_re(url, site_key) == bfs  # TODO Fix this test


def test_deathbycaptcha() -> None:
    # Death By Captcha
    dbc = BotDeathByCaptchaPlugin(os.getenv("DBC_USERNAME"), os.getenv("DBC_PASSWORD"))
    assert dbc.solve(os.path.join(cur_dir, "captcha_ms.jpeg")) == '56nn2'
