#!/usr/bin/env python
__author__ = 'usama'
''' A Simple Ros Node to publish odometry from gridmap and odom '''
import rospy
import rospkg
from nav_msgs.msg import Odometry
import numpy as np
import tf
from tf import TransformListener

# global vars
pub = None
tlisten = None
_base_frame_name = None
_map_frame_name = None

def callback_odom(data):
    # get current transorm
    if tlisten.frameExists(_base_frame_name) and tlisten.frameExists(_map_frame_name):
        _t = tlisten.getLatestCommonTime(_base_frame_name, _map_frame_name)
        try:
            position, quaternion = tlisten.lookupTransform(_map_frame_name, _base_frame_name, rospy.Time())
        except tf.ExtrapolationException as e:
            rospy.logwarn('Extrapolation Warning')
            return None
        # publish odom
        _msg = Odometry()        
        _msg.header = data.header
        _msg.header.frame_id = _map_frame_name
        _msg.child_frame_id = _base_frame_name
        _msg.pose.pose.orientation.x = quaternion[0]
        _msg.pose.pose.orientation.y = quaternion[1]
        _msg.pose.pose.orientation.z = quaternion[2]
        _msg.pose.pose.orientation.w = quaternion[3]
        _msg.pose.pose.position.x = position[0]
        _msg.pose.pose.position.y = position[1]
        _msg.pose.pose.position.z = position[2]
        _msg.twist.twist.linear.x = data.twist.twist.linear.x
        _msg.twist.twist.angular.z = data.twist.twist.linear.x
        pub.publish(_msg)  
    else:
        rospy.logwarn('Frame does not exist : %s, %s', _base_frame_name, _map_frame_name)

if __name__ == '__main__':
    rospy.init_node('odompublisher', anonymous=False)
    rospy.loginfo('Starting odometry publishing node')
    # get parameters
    _base_frame_name = rospy.get_param('~base_frame', default='base_link')
    _map_frame_name = rospy.get_param('~map_frame', default='map')
    # remap parameters
    _odom_name = rospy.remap_name('odom')
    _odom_repub_name = rospy.remap_name('odom2')
    # Publishers
    pub = rospy.Publisher(_odom_repub_name, Odometry, queue_size=10)
    rospy.loginfo('Publishing odometry to %s', _odom_repub_name)
    # Initialize Listener
    tlisten = TransformListener()
    # Subscirbers
    rospy.Subscriber(_odom_name, Odometry, callback_odom)
    rospy.loginfo('Subscribed to %s', _odom_name)
    # spin
    rospy.spin()
    # shutdown
    rospy.loginfo('Shutting Down')
