 #!/bin/bash

for i in /eos/cms/store/user/ktos/rValues/*;
do
  eos ls $i > OUTPUT_${i##*rValues/}.out
done
