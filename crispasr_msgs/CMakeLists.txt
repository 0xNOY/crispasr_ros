cmake_minimum_required(VERSION 3.10)
project(crispasr_msgs)

set(MSG_FILES
  AudioData.msg
  SpeechResult.msg
)

if("$ENV{ROS_VERSION}" STREQUAL "1")
  find_package(catkin REQUIRED COMPONENTS
    message_generation
    std_msgs
  )

  add_message_files(FILES ${MSG_FILES})

  generate_messages(DEPENDENCIES std_msgs)

  catkin_package(CATKIN_DEPENDS message_runtime std_msgs)
else()
  find_package(ament_cmake REQUIRED)
  find_package(rosidl_default_generators REQUIRED)
  find_package(std_msgs REQUIRED)

  set(INTERFACE_FILES)
  foreach(file ${MSG_FILES})
    list(APPEND INTERFACE_FILES "msg/${file}")
  endforeach()

  rosidl_generate_interfaces(${PROJECT_NAME}
    ${INTERFACE_FILES}
    DEPENDENCIES std_msgs
  )

  ament_export_dependencies(rosidl_default_runtime)
  ament_package()
endif()
