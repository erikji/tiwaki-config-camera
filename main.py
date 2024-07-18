from onvif import ONVIFCamera
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='config framerate and resolution on ONVIF-supported camera')
    parser.add_argument('ip_address')
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('-p', '--port', default=80, help='HTTP port')
    args = parser.parse_args()
    mycam = ONVIFCamera(args.ip_address, args.port, args.username, args.password, 'wsdl')
    mycam.create_media_service()    
    options = mycam.media.GetVideoEncoderConfigurationOptions()

    validEncodings = []
    for encoding in ['JPEG', 'MPEG4', 'H264']:
        if options[encoding] != None:
            validEncodings.append(encoding)

    for encoding in validEncodings:
        print(f'Resolutions for {encoding}: ')
        for resolution in options[encoding].ResolutionsAvailable:
            print(f'\t {resolution.Width}x{resolution.Height}')
        print(f'Framerates for {encoding}: {options[encoding].FrameRateRange}')
        print()

    allConfigs = mycam.media.GetVideoEncoderConfigurations()
    if len(allConfigs) < 1:
        print('No configurations found')
        exit()
    currentConfig = allConfigs[0]
    print(f'Current configuration {currentConfig.Name}: {currentConfig.Encoding}, {currentConfig.Resolution.Width}x{currentConfig.Resolution.Height}, {currentConfig.RateControl.FrameRateLimit} max FPS')

    print(f'\nEditing configuration {currentConfig.Name}')

    encoding = validEncodings[int(input(f'Select one of {validEncodings}, type one of {list(range(len(validEncodings)))} '))]
    currentConfig.Encoding = encoding

    currentConfig.Resolution = options[encoding].ResolutionsAvailable[int(input(f'Select one of {[f"{resolution.Width}x{resolution.Height}" for resolution in options[encoding].ResolutionsAvailable]}, type one of {list(range(len(options[encoding].ResolutionsAvailable)))} '))]

    currentConfig.RateControl.FrameRateLimit = int(input(f'Select integer framerate between {options[encoding].FrameRateRange.Min}, {options[encoding].FrameRateRange.Max} '))

    setEncoderConfigParams = mycam.media.create_type('SetVideoEncoderConfiguration')
    setEncoderConfigParams.Configuration = currentConfig
    setEncoderConfigParams.ForcePersistence = True # Deprecated but still required param?
    
    mycam.media.SetVideoEncoderConfiguration(setEncoderConfigParams)
    print('done')