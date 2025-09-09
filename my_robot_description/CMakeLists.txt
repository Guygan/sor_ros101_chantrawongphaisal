# ... (เนื้อหาเดิมของไฟล์ CMakeLists.txt) ...

# --- เพิ่มส่วนนี้เข้าไป ---
# Install launch files
install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# Install URDF and mesh files
install(
  DIRECTORY urdf
  DESTINATION share/${PROJECT_NAME}
)
install(
  DIRECTORY meshes
  DESTINATION share/${PROJECT_NAME}
)

# Install RViz config files
install(
  DIRECTORY rviz
  DESTINATION share/${PROJECT_NAME}
)

# Install config files (YAML, etc.)
# บรรทัดนี้สำคัญที่สุดในการแก้ปัญหา EKF และ SLAM
install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
