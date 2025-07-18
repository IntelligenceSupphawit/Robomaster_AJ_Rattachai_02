import time
import robomaster
import csv
from datetime import datetime
from robomaster import robot

logging_enabled = False  # ป้องกันการบันทึกข้อมูลก่อนเริ่มต้น

# บันทึกข้อมูลลงไฟล์ CSV

sensor_state = {
    "timestamp": None,
    "distance": None,
    "pitch_angle": None,
    "yaw_angle": None,
    "pitch_ground_angle": None,
    "yaw_ground_angle": None,
}


fieldnames = list(sensor_state.keys())
csv_file = open('Data.csv', 'w', newline='')
csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
csv_writer.writeheader()
def update_and_log(**kwargs):
    global sensor_state
    if not logging_enabled:
        return  # ไม่บันทึกข้อมูลหาก logging enabled = false

    sensor_state.update(kwargs)
    sensor_state['timestamp'] = datetime.now().strftime('%H:%M:%S.%f')
    csv_writer.writerow(sensor_state)
    csv_file.flush()


# ส่วนบันทึก Callcack Data
def sub_data_handler_dis(sub_info):
    distance = sub_info
    print("tof1:{0}".format(distance[0]))

    update_and_log(distance=distance[0])

def sub_data_handler_ang(angle_info):
    pitch_angle, yaw_angle, pitch_ground_angle, yaw_ground_angle = angle_info
    print("gimbal angle: pitch_angle:{0}, yaw_angle:{1}, pitch_ground_angle:{2}, yaw_ground_angle:{3}".format(
        pitch_angle, yaw_angle, pitch_ground_angle, yaw_ground_angle))

    update_and_log(pitch_angle=pitch_angle, yaw_angle = yaw_angle, pitch_ground_angle=pitch_ground_angle, yaw_ground_angle=yaw_ground_angle)

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

# เริ่มบันทึกข้อมูลลง CSV เมื่อหุ่นเริ่มทำงานเท่านั้น
    logging_enabled = True

    ep_gimbal = ep_robot.gimbal
    ep_sensor = ep_robot.sensor

    ep_gimbal.moveto(pitch=0, yaw=0, yaw_speed=10).wait_for_completed() #รีหน้าตรง
    ep_gimbal.moveto(yaw=90 ,yaw_speed=10).wait_for_completed() #หมุนขวา

    ep_sensor.sub_distance(freq=5, callback=sub_data_handler_dis)
    ep_gimbal.sub_angle(freq=5, callback=sub_data_handler_ang)
    # time.sleep(60)
   
    ep_gimbal.moveto(yaw=-90 ,yaw_speed=10).wait_for_completed() #หมุนซ้าย

    logging_enabled = False  # หยุดบันทึกข้อมูลเมื่อเสร็จสิ้นการเคลื่อนที่

    ep_sensor.unsub_distance()
    ep_gimbal.unsub_angle()
    
    ep_gimbal.moveto(pitch=0, yaw=0, yaw_speed=10).wait_for_completed() #รีหน้าตรง

    ep_robot.close()
    csv_file.close()
