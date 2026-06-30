cmake_minimum_required(VERSION 3.10)
project(crispasr_ros)

if("$ENV{ROS_VERSION}" STREQUAL "1")
  find_package(catkin REQUIRED)

  catkin_python_setup()

  catkin_package()

  catkin_install_python(PROGRAMS
    scripts/crispasr_node
    scripts/audio_publisher_node
    scripts/microphone_node
    scripts/confirmation_ros_demo
    scripts/hsr_ssh_asr_demo
    DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
  )

  install(DIRECTORY launch config
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
  )
else()
  find_package(ament_cmake REQUIRED)
  find_package(ament_cmake_python REQUIRED)

  ament_python_install_package(crispasr_ros PACKAGE_DIR src/crispasr_ros)

  install(PROGRAMS
    scripts/crispasr_node
    scripts/audio_publisher_node
    scripts/microphone_node
    scripts/confirmation_ros_demo
    scripts/hsr_ssh_asr_demo
    DESTINATION lib/${PROJECT_NAME}
  )

  install(DIRECTORY launch config
    DESTINATION share/${PROJECT_NAME}
  )

  ament_package()
endif()
