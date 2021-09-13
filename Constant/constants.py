# -----------------------
# sys config

work_dir = "/tmp"
request_success = "Success"
request_failed = "Failed"

# -----------------------
# component config
file_server_url = "http://frext-file-svc:8010/"

# -----------------------
# for request compile files
tcls_API = "tcls"
tcls_suffix = ".tcl"

questions_API = "questions"
questions_suffix = ".zip"

tests_API = "tests"
tests_suffix = ".v"

bits_API = "bits"
bits_suffix = ".bit"

logs_API = "logs"
logs_suffix = ".log"

c_userId = "userId"
c_testId = "testId"
c_submitId = "submitId"
c_topic = "topic"
c_topModuleName = "topModuleName"
c_tcl = "tcl"
c_file_server_url = "fileServerUrl"

# -----------------------
# for return compile status/result
status_API = "compile_status"
result_API = "result_status"

c_compile_server_url = "compileServerUrl"

# -----------------------
# other constants, maybe configurable in future
compileScript = "compile/compile.sh"
vivado = "/tools/Xilinx/Vivado/2020.1/bin/vivado"
FPGAVersion = "xc7k160tffg676-2L"
compileThread = "4"
