set(PYQT_MAJOR 4)
set(PYQT_MINOR 8)
set(PYQT_PATCH 3)
set(PYQT_MAJOR_SRC 4)
set(PYQT_MINOR_SRC 10)
set(PYQT_PATCH_SRC 1)
set(PYQT_VERSION ${PYQT_MAJOR_SRC}.${PYQT_MINOR_SRC}.${PYQT_PATCH_SRC})
set(PYQT_URL ${LLNL_URL})
set(PYQT_GZ_APPLE PyQt-mac-gpl-${PYQT_VERSION}.tar.gz)
set(PYQT_GZ_UNIX PyQt-x11-gpl-${PYQT_VERSION}.tar.gz)
set(PYQT_MD5_APPLE f8feb678212cf4f84d5cf5317b1f5bc2 )
set(PYQT_MD5_UNIX e5973c4ec0b0469f329bc00209d2ad9c )
set(PYQT_SOURCE ${PYQT_URL}/${PYQT_GZ_${CMAKE_PLATFORM}})
set(PYQT_MD5 ${PYQT_MD5_${CMAKE_PLATFORM}})

add_sb_package(NAME PyQt GROUPS "GRAPHICS" DEFAULT ON)
