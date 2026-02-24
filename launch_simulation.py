from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
from pathlib import Path

def generate_launch_description():
    pkg_dir = get_package_share_directory('gazebo_uav_simulation')
    
    urdf_file = os.path.join(pkg_dir, 'urdf', 'uav_model.urdf')
    world_file = os.path.join(pkg_dir, 'worlds', 'uav_world.world')
    
    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=world_file,
        description='SDF world file'
    )
    
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_file}.items(),
    )
    
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gzclient.launch.py')
        ),
    )
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'robot_description': open(urdf_file).read()
        }],
    )
    
    spawn_uav = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'quadrotor',
            '-file', urdf_file,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '1.0',
        ],
        output='screen',
    )

    uav_controller = Node(
        package='gazebo_uav_simulation',
        executable='uav_controller',
        name='uav_controller',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'max_velocity': 5.0,
            'max_altitude': 100.0,
        }],
    )

    imu_publisher = Node(
        package='gazebo_uav_simulation',
        executable='imu_publisher',
        name='imu_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'update_rate': 50.0,
        }],
    )

    camera_publisher = Node(
        package='gazebo_uav_simulation',
        executable='camera_publisher',
        name='camera_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'image_width': 640,
            'image_height': 480,
            'update_rate': 30.0,
        }],
    )

    tf_broadcaster = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'base_link'],
        output='screen',
    )

    teleop_node = Node(
        package='gazebo_uav_simulation',
        executable='keyboard_teleop',
        name='keyboard_teleop',
        output='screen',
        prefix='xterm -e',
    )

    rviz_config = os.path.join(pkg_dir, 'rviz', 'uav_config.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    ld = LaunchDescription([
        use_sim_time,
        world_arg,
        gazebo_server,
        gazebo_client,
        robot_state_publisher,
        spawn_uav,
        uav_controller,
        imu_publisher,
        camera_publisher,
        tf_broadcaster,
        rviz,

    ])
    
    return ld
