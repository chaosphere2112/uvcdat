set(UVCMETRICS_TAG 790a22a00d57e2ddaeffbb79b869df169a626204)

set (nm UVCMETRICS)
string(TOUPPER ${nm} uc_nm)
set(${uc_nm}_VERSION ${${nm}_TAG})
set(UVCMETRICS_URL ${LLNL_URL})
set(UVCMETRICS_ZIP uvcmetrics-${UVCMETRICS_VERSION}.zip)
#set(UVCMETRICS_SOURCE ${UVCMETRICS_URL}/${UVCMETRICS_ZIP})
set(UVCMETRICS_SOURCE ${GIT_PROTOCOL}github.com/UV-CDAT/uvcmetrics.git )
set(UVCMETRICS_MD5)
set(UVCMETRICS_BRANCH uvcdat-2.1.0)
#set(GIT_TAG 1808453d1cac69e54761521a3e1519b099f34c35)

add_cdat_package_dependent(UVCMETRICS "" "" ON "CDAT_BUILD_GUI" OFF)

