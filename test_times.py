from wa_counties import get_city_drive_time, get_drive_time

def fmt(s):
    if s is None:
        return 'None'
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h}h {m}m {sec}s"

print('Republic->Davenport city seconds:', get_city_drive_time('Republic','Davenport'))
print('Republic->Davenport formatted:', fmt(get_city_drive_time('Republic','Davenport')))
print('Ferry->Lincoln county seconds:', get_drive_time('Ferry','Lincoln'))
print('Ferry->Lincoln formatted:', fmt(get_drive_time('Ferry','Lincoln')))
print('Seattle->Bellevue city seconds:', get_city_drive_time('Seattle','Bellevue'))
print('Seattle->Bellevue formatted:', fmt(get_city_drive_time('Seattle','Bellevue')))
