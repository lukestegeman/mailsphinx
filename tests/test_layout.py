import mailsphinx.utils.build_text as bt


import freezegun
import sys
import os

import pandas as pd
import datetime



if __name__ == '__main__':

    actual_now = datetime.datetime.now()
    with freezegun.freeze_time('2024-01-08'):

        # FOR TESTING -- SAVES THE HTML FILE FOR CHECKING
        frozen_now = datetime.datetime.now()

        if actual_now > frozen_now:
            historical = True
        else:
            historical = False

        start_datetime = datetime.datetime(year=2024, month=1, day=1).replace(tzinfo=datetime.timezone.utc)
        end_datetime = datetime.datetime(year=2024, month=1, day=8).replace(tzinfo=datetime.timezone.utc)
        html = bt.build_text(historical, convert_images_to_base64=False, start_datetime=start_datetime, end_datetime=end_datetime)


        a = open('test.html', 'w')
        a.write(html)
        a.close()
