#!/usr/bin/env python
# -*- encode: utf-8 -*-

#Copyright 2015 RAPP

#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at

    #http://www.apache.org/licenses/LICENSE-2.0

#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

# Authors: Aris Thallas
# contact: aris.thallas@{iti.gr, gmail.com}

import os
from scipy.io import wavfile

## @class TransformAudio
# @brief Provides audio type tranformation functionalities
#
# Allows the transformation of an audio file to a different format. Supports
# the alteration of the type (i.e. headset, nao_wav_1_ch etc.), the sample
# rate, the audio channel number, the audio format and the audio name.
# Handles transform audio service callback
# (rapp_audio_processing.rapp_audio_processing.AudioProcessing::transform_audio)
class TransformAudio:

    ## @brief Performs the audio transformation
    # @param source_type [string] The source audio file's type
    # @param source_name [string] The source audio file's name
    # @param target_type [string] The target audio file's type
    # @param target_name [string] The target audio file's name
    # @param target_channels [string] The target audio's channel number
    # @param target_rate [string] The target audio's sample rate
    #
    # @return status [string] The status of the transformation prcedure
    # @return filename [string] The name of the produced file
    def transform_audio(self, source_type, source_name, \
            target_type, target_name, target_channels, target_rate ):

        try:
            self._assertArgs( source_type, source_name, target_type, \
                    target_name, target_channels, target_rate )
        except Exception as e:
            return [ str(e), '' ]

        try:
            self._validateSourceType( source_type, source_name )
        except Exception as e:
            return [ str(e), '' ]

        try:
            self._convertType( source_type, source_name, target_type, \
                    target_name, target_channels, target_rate )
        except Exception as e:
            return [ str(e), '' ]

        return [ 'success', target_name ]

    ## @brief Verifies the existence of the required arguments
    # @param source_type [string] The source audio file's type
    # @param source_name [string] The source audio file's name
    # @param target_type [string] The target audio file's type
    # @param target_name [string] The target audio file's name
    # @param target_channels [string] The target audio's channel number
    # @param target_rate [string] The target audio's sample rate
    #
    # @exception Exception Arguments are invalid
    def _assertArgs(self, source_type, source_name, target_type, target_name, \
            target_channels, target_rate ):

        if not os.path.isfile( source_name ):
            raise Exception( "Error: file \'" + source_name + '\' not found' )
        if target_name == '':
            raise Exception( "Error: target filename not provided" )
        if target_type == '':
            raise Exception( "Error: target type not provided" )
        if target_rate < 0:
            raise Exception( "Error: target_rate can not be negative" )
        if target_channels < 0:
            raise Exception( "Error: target_channels can not be negative" )
        if target_channels > 8:
            raise Exception( "Error: target_channels can not be greater than 8" )

    ## @brief Performs audio conversion
    # @param source_type [string] The source audio file's type
    # @param source_name [string] The source audio file's name
    # @param target_type [string] The target audio file's type
    # @param target_name [string] The target audio file's name
    # @param target_channels [string] The target audio's channel number
    # @param target_rate [string] The target audio's sample rate
    #
    # @exception Exception Conversion malfunction
    def _convertType(self, source_type, source_name, target_type, target_name, \
            target_channels, target_rate ):

        channels = ''
        rate = ''
        if target_type == 'flac':
            if target_channels != 0:
                channels = '--channels=' + str( target_channels )
            if target_rate != 0:
                rate = '--sample-rate=' + str( target_rate )

            command = 'flac -f ' + channels + ' ' + rate + " " + source_name + \
                ' -o ' + target_name + " --totally-silent --channel-map=none"
            flac_status = os.system( command )


            if os.path.isfile( target_name ) != True or flac_status != 0 :
                raise Exception( "Error: flac command malfunctioned. File path was"\
                        + source_name )
        else:
            if target_channels != 0:
                channels = '-c ' + str( target_channels )
            if target_rate != 0:
                rate = '-r ' + str( target_rate )
            command = "sox " + source_name + " " + channels + " " + rate + \
                    " " + target_name

            sox_status = os.system( command )

            if os.path.isfile( target_name ) != True or sox_status:
                raise Exception( "Error: SoX malfunctioned. File path was" + \
                        source_name )


    ## @brief Validates that the provided audio type match the file extension
    # @param source_type [string] The source audio file's type
    # @param name [string] The source audio file's name
    #
    # @exception Exception Audio type/file type mismatch
    def _validateSourceType( self, source_type, name ):

        [ source_file_name, source_extention ] = os.path.splitext( name )

        if source_type == 'nao_ogg':
            if source_extention != '.ogg':
                raise Exception( "Error: ogg type selected but file is of another type" )

        elif source_type == "nao_wav_1_ch" or source_type == 'headset':
            if source_extention != ".wav":
                raise Exception( "Error: wav type 1 channel selected but file is of another type" )

            samp_freq, signal = wavfile.read( name )
            if len( signal.shape ) != 1:
                error = ("Error: wav 1 ch declared but the audio file has " +\
                str(signal.shape[1]) + ' channels')
                raise Exception( error )

        elif source_type == "nao_wav_4_ch":
            if source_extention != ".wav":
                raise Exception( "Error: wav type 4 channels selected but file is of another type" )

            samp_freq, signal = wavfile.read( name )
            if len(signal.shape) != 2 or signal.shape[1] != 4:
                raise Exception( "Error: wav 4 ch declared but the audio file has not 4 channels" )

        else:
            raise Exception( "Non valid noise audio type" )
