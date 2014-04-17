set(TIFF_MAJOR 3)
set(TIFF_MINOR 9)
set(TIFF_PATCH 4)
set(TIFF_URL ${LLNL_URL})
set(TIFF_GZ tiff-${TIFF_MAJOR}.${TIFF_MINOR}.${TIFF_PATCH}.tar.gz)
set(TIFF_MD5 2006c1bdd12644dbf02956955175afd6)
set(TIFF_SOURCE ${TIFF_URL}/${TIFF_GZ})

set (nm TIFF)
string(TOUPPER ${nm} uc_nm)
set(${uc_nm}_VERSION ${${nm}_MAJOR}.${${nm}_MINOR}.${${nm}_PATCH})

add_sb_package(NAME tiff GROUPS "GRAPHICS" DEFAULT ON)
