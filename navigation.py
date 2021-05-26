#!/usr/bin/env python3

import rospy
import random
from time import sleep
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion
from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseActionResult
from tf.transformations import quaternion_from_euler
from geometry_msgs.msg import PoseWithCovarianceStamped


def talker_main(x, y, theta):
    
    pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
    rate = rospy.Rate(5)

    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.pose.position.x = x
    pose.pose.position.y = y
    quat = quaternion_from_euler(0, 0, theta)
    pose.pose.orientation.x = quat[0]
    pose.pose.orientation.y = quat[1]
    pose.pose.orientation.z = quat[2]
    pose.pose.orientation.w = quat[3]
    
    if not rospy.is_shutdown():
        pub.publish(pose)
        rate.sleep()
        pub.publish(pose)


def listener_status(data):
    
    global status

    status = data.status.status


def define_next_y():

    global needs_new_y
    global next_y
    global previous_y

    if needs_new_y == True:

        next_y = previous_y + track_width_y
        needs_new_y = False

    elif needs_new_y == False:

        next_y = previous_y
        needs_new_y = True


def define_track_width():

    global tracks
    global track_width_y

    track_width_y = round((6 / tracks), 1)


def execute_main():

    global status

    global up_down
    global needs_new_y

    global tracks
    global track_width_y

    global previous_y

    tracks = eval(input("Digite a quantidade de faixas na areia: "))
    tracks = int(tracks)

    define_track_width()

    sleep(3)
    talker_main(-3.1, -3.0, 0.0)
    sleep(3)

    for _ in (number + 1 for number in range(((tracks * 2) + 2))):

        x = 0.0
        y = next_y
        z = random.uniform(0.0, 6.28)

        if _ == 1:

            talker_main(-2.9, -3.0, 0.0)
            sleep(3)

            x = 3.0
            y = -3.0
            up_down = True
            needs_new_y = True

        elif _ != 1 and _ % 2 == 0: # Even position

            if up_down == True:

                x = 3.0
                up_down = True
                needs_new_y = False

            elif up_down == False:

                x = -3.0
                up_down = False
                needs_new_y = False

        elif _ != 1 and _ % 2 != 0: # Odd Position

            if up_down == True:

                x = -3.0
                up_down = False
                needs_new_y = True

            elif up_down == False:

                x = 3.0
                up_down = True
                needs_new_y = True

        previous_y = y

        talker_main(x, y, z)
        
        sleep(5)

        while status != 3:
            rospy.Subscriber('/move_base/result', MoveBaseActionResult, listener_status)
            if status == 3:
                break

        define_next_y()

        # Trash collection state
        sleep(5)


status = 0

next_y = 0.0
previous_y = 0.0

up_down = True
needs_new_y = True

tracks = 0
track_width_y = 0.0

rospy.init_node('pose_goal', anonymous=True)


if __name__ == '__main__':
    execute_main()
