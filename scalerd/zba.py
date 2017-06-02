#!/usr/bin/env python3


"""
   Copyright 2017 Andris Zbitkovskis

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import math
import argparse
import daemon
import signal 
import logging
import configparser 

from daemon import pidfile 
from weigherstate import WeigherState
from scaler import Scaler

debug =True


def start_daemon(pidf, logf, workd, rndf, fork ,amqp_url):
    global debug
    interactive =  not fork  in ['y', 'Y']
    LOG_FILE='/var/log/scaler/daemon.log'
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s","%Y-%m-%d %H:%M:%S")
    fh = logging.StreamHandler() if interactive else logging.FileHandler(LOG_FILE) 
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    result_file=open(logf,'a')
    scaler = Scaler(result_file , rndf,logger,amqp_url= amqp_url)
    if not interactive :
        if debug:
            print("scaler: entered run()")
            print("scaler: pidf:{} logf:{} workd: {} rndf: {} fork:{} ".format(pidf, logf,workd,rndf, fork))
            print("scaler: about to start daemonization")
        scaler.daemon=True
        ctx=daemon.DaemonContext(
            working_directory=workd ,
            umask=0o002,
            pidfile=pidfile.TimeoutPIDLockFile(pidf),
            )
        ctx.files_preserve=[fh.stream,result_file ]
        ctx.signal_map = {
            signal.SIGHUP: 'terminate',
            }
        ctx.stdout=fh.stream 
        ctx.stderr=fh.stream 
        with ctx:
               scaler.run()
    else:
        scaler.run()
        
 

def main(argv):
   pass 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ceph Scaler daemon")
    parser.add_argument('-p', '--pid-file', default='/var/run/scaler/scaler.pid')
    parser.add_argument('-l', '--log-file', default='/var/log/scaler/scaler.log')
    parser.add_argument('-w', '--working-dir', default='/var/lib/scaler')
    parser.add_argument('-r', '--rnd-table', default='/var/lib/scaler/rndtable.txt')
    parser.add_argument('-f', '--fork', choices=['y','n'] , default='y',  help='Fork' )
    args = parser.parse_args()
    configParser = configparser.RawConfigParser()   
    configFilePath = '/etc/scaler.cfg'
    configParser.read(configFilePath)

    host=configParser.get('amqp', 'host')
    user=configParser.get('amqp', 'user')
    password=configParser.get('amqp', 'password')
    amqp_url="amqp://{}:{}@{}:5672/%2F".format(user,password,host)
    start_daemon(pidf=args.pid_file, logf=args.log_file,workd = args.working_dir,rndf = args.rnd_table , fork=args.fork , amqp_url=amqp_url)
   # main(sys.argv)



