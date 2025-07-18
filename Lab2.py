# นำเข้าโมดูลที่ต้องการใช้งาน
import time
import robomaster
import csv
from datetime import datetime
from robomaster import robot

logging_enabled = False  # ป้องกันการบันทึกข้อมูลก่อนเริ่มต้น

# ส่วนบันทึกข้อมูลลงไฟล์ CSV

# สร้างตัวแปรเก็บ State Sensor
sensor_state = {
    "timestamp": None,
    "distance": None,
    "pitch_angle": None,
    "yaw_angle": None,
    "pitch_ground_angle": None,
    "yaw_ground_angle": None,
}

# สร้างไฟล์ CSV เเละการตั้งค่า
fieldnames = list(sensor_state.keys()) # สร้าง fieldnames จาก sensor_state
csv_file = open('Data.csv', 'w', newline='') # เปิดไฟล์ CSV สำหรับเขียนข้อมูล
csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames) # สร้าง writer สำหรับเขียนข้อมูลลงไฟล์ CSV
csv_writer.writeheader() # เขียน header ลงไฟล์ CSV

# ฟังก์ชันอัพเดทค่า logและบันทึกลงไฟล์ CSV
def update_and_log(**kwargs):
    global sensor_state # ใช้ตัวแปร global เพื่อเข้าถึง sensor_state
    if not logging_enabled: 
        return  # ไม่บันทึกข้อมูลหาก logging enabled = false

    # อัพเดทค่า sensor_state ด้วยข้อมูลที่ได้รับ
    sensor_state.update(kwargs)

    # อัพเดทค่า timestamp ทุกครั้งที่มีการบันทึกข้อมูล
    sensor_state['timestamp'] = datetime.now().strftime('%H:%M:%S.%f')
    csv_writer.writerow(sensor_state)
    csv_file.flush() 


# ส่วนบันทึกและแสดง Callcack Data ของ distance
def sub_data_handler_dis(sub_info):
    distance = sub_info
    print("tof1:{0}".format(distance[0])) # แสดงระยะทางที่วัดได้จาก sensor ที่ Terminal

    update_and_log(distance=distance[0]) # บันทึกระยะทางที่วัดได้จาก sensor

# ส่วนบันทึกและแสดง Callcack Data ขององศาการหมุนของ gimbal
def sub_data_handler_ang(angle_info):
    pitch_angle, yaw_angle, pitch_ground_angle, yaw_ground_angle = angle_info
    print("gimbal angle: pitch_angle:{0}, yaw_angle:{1}, pitch_ground_angle:{2}, yaw_ground_angle:{3}".format(
        pitch_angle, yaw_angle, pitch_ground_angle, yaw_ground_angle)) # แสดงองศาการหมุนของ gimbal ที่ Terminal

    update_and_log(pitch_angle=pitch_angle, yaw_angle = yaw_angle, pitch_ground_angle=pitch_ground_angle, yaw_ground_angle=yaw_ground_angle) # บันทึกองศาการหมุนของ gimbal ลงไฟล์ CSV

if __name__ == '__main__': # ส่วนของ main function
    ep_robot = robot.Robot() #สร้าง object ของหุ่นยนต์
    ep_robot.initialize(conn_type="ap") # เชื่อมต่อหุ่นยนต์ผ่าน Wi-Fi แบบ Access Point

# เริ่มบันทึกข้อมูลลง CSV เมื่อหุ่นเริ่มทำงานเท่านั้น
    logging_enabled = True

    ep_gimbal = ep_robot.gimbal # สร้าง object ของ gimbal
    ep_sensor = ep_robot.sensor # สร้าง object ของ sensor

    ep_gimbal.moveto(pitch=0, yaw=0, yaw_speed=10).wait_for_completed() #รีเช็ตหน้า gimbal ให้ตรง
    ep_gimbal.moveto(yaw=90 ,yaw_speed=10).wait_for_completed() #หมุนทางขวา gimbal 90 องศา

    ep_sensor.sub_distance(freq=5, callback=sub_data_handler_dis) #เปิดใช้งาน sensor เพื่อวัดระยะวัตถุตรงหน้า
    ep_gimbal.sub_angle(freq=5, callback=sub_data_handler_ang) #บันทึกองศาการหมุนของ gimbal
    # time.sleep(60)
   
    ep_gimbal.moveto(yaw=-90 ,yaw_speed=10).wait_for_completed() #หมุนทางซ้าย gimbal 90 องศา

    logging_enabled = False  # หยุดบันทึกข้อมูลเมื่อเสร็จสิ้นการเคลื่อนที่

    ep_sensor.unsub_distance() # หยุดเก็บข้อมูล sensor ที่ใช้วัดระยะทาง
    ep_gimbal.unsub_angle() # หยุดเก็บข้อมูล sensor ที่ใช้เก็บองศาการหมุนของ gimbal
    
    ep_gimbal.moveto(pitch=0, yaw=0, yaw_speed=10).wait_for_completed() #รีเช็ตหน้า gimbal ให้ตรง

    ep_robot.close() # ปิดการใช้งานหุ่นยนต์
    csv_file.close() # ปิดการบันทึก file csv
