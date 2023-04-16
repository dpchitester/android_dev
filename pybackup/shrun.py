import subprocess
import utils
import re

proc = subprocess.run(tcmd, shell=self.shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
self.outs += proc.stdout.decode()
self.outs = re.sub(r"\r\n", "\n", self.outs)
self.returncode = proc.returncode
