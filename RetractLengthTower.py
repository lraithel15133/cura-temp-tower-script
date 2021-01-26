# -*- coding: utf-8 -*-

import json
import re

from ..Script import Script


class RetractLengthTower(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return json.dumps({
            'name': 'Retraction Length Tower',
            'key': 'RetractLengthTower',
            'metadata': {},
            'version': 2,
            'settings': {
                'start_retract': {
                    'label': 'Start Retraction Length',
                    'description': '',
                    'unit': 'mm',
                    'type': 'float',
                    'default_value': 1
                },
                'height_increment': {
                    'label': 'Height Increment',
                    'description': (
                        'Adjust Length each time height param '
                        'changes by this much'
                    ),
                    'unit': 'mm',
                    'type': 'float',
                    'default_value': 10
                },
                'retract_increment': {
                    'label': 'Retraction Length Increment',
                    'description': (
                        'Increase length by this much with each height increment. '
                        'Use negative values to decrease with height'
                    ),
                    'unit': 'mm',
                    'type': 'float',
                    'default_value': .2
                },
                'start_height': {
                    'label': 'Start Height ',
                    'description': (
                        'Start the retraction tower at this height.'
                    ),
                    'unit': 'mm',
                    'type': 'float',
                    'default_value': 1.4
                }
            }
        })

    def execute(self, data):
        start_retract = self.getSettingValueByKey('start_retract')
        height_inc = self.getSettingValueByKey('height_increment')
        retract_inc = self.getSettingValueByKey('retract_increment')
        start_height = self.getSettingValueByKey('start_height')

        cmd_re = re.compile(
            r'G[0-9]+ '
            r'(?:F[0-9]+ )?'
            r'X[0-9]+\.?[0-9]* '
            r'Y[0-9]+\.?[0-9]* '
            r'Z(-?[0-9]+\.?[0-9]*)'
        )

        # Set initial state
        current_retract = 0
        started = False
        for i, layer in enumerate(data):
            lines = layer.split('\n')
            for j, line in enumerate(lines):
                # Before ;LAYER:0 arbitrary setup GCODE can be run.
                if line == ';LAYER:0':
                    started = True
                    continue

                # skip comments and startup lines
                if line.startswith(';') or not started:
                    continue

                # Find any X,Y,Z Line (ex. G0 X60.989 Y60.989 Z1.77)
                match = cmd_re.match(line)
                if match is None:
                    continue
                z = float(match.groups()[0])
				
                if z < start_height:
                    continue
				
                new_retract = ((start_retract) + (int((z - start_height) / height_inc)) * (retract_inc))

                if new_retract != current_retract:
                    current_retract = new_retract
                    lines[j] += '\n;TYPE:CUSTOM\nM207 S%f' % new_retract
            data[i] = '\n'.join(lines)

        return data
