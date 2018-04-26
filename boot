#!/bin/bash

automake --foreign -c -a 
autoreconf -i
automake --foreign -c -a 
