
                    if [[ $(grep -c "$(cat mykey-rsa.pub)" ~/.ssh/authorized_keys) == 0 ]]; then
                        cat /home/laura/mykey-rsa.pub >> .ssh/authorized_keys
                    else
                       echo "key already present"
                    fi
                    
