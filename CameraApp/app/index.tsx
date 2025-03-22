import { Text, View, StyleSheet, Button, TouchableOpacity, Pressable } from "react-native";
import { Image } from 'expo-image';
import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { useRef, useState } from 'react';

export default function Index() {

    let cameraRef = useRef<CameraView>(null);

    const [facing, setFacing] = useState<CameraType>('back');
    const [cameraPermission, requestCameraPermission] = useCameraPermissions();
    const [photo, setPhoto] = useState<string | undefined>();

    if(!cameraPermission) {
        return <View />
    }

    if (!cameraPermission.granted) {
        return(
            <View style={styles.container}>
                <Text style={styles.message}>We need your permission to show the camera</Text>
                <Button onPress={requestCameraPermission} title="grant permission" />
            </View>
        );
    }

    function toggleCameraFacing() {
        setFacing(current => (current === 'back' ? 'front' : 'back'));
    }


    let takePic = async() => {
        const newPhoto = await cameraRef.current?.takePictureAsync();
        setPhoto(newPhoto?.uri);    
    }

    const renderImage = () => {
        return(
            <View>
                <Image
                    source={ photo }
                    contentFit="contain"
                    style={{ width: 300, aspectRatio: 1 }}
                />
                <Button onPress={() => setPhoto(undefined)} title="Take another picture" />
            </View>
        );
    };

    const renderCamera = () => {
        return(
            <CameraView style={styles.camera} facing={facing} ref={cameraRef}>
                <View style={styles.buttonContainer}>
                    <TouchableOpacity style={styles.button} onPress={toggleCameraFacing}>
                        <Text style={styles.text}>Flip Camera</Text>
                    </TouchableOpacity>
                </View>
                <Pressable onPress={takePic} style={{
                    backgroundColor: 'white',
                    paddingVertical: 12,
                    paddingHorizontal: 30,
                    borderRadius: 30
                }} >
                    <Text>Take a Pic</Text>
                </Pressable>
            </CameraView>
        )
    };

    return (
        <View style={styles.container}>
            {photo ? renderImage() : renderCamera()}
        </View>
    );
}

const styles = StyleSheet.create({
    container : {
        flex : 1,
        justifyContent : 'center',
    },
    camera: {
        flex: 1,
    },    
    buttonContainer : {
        flex: 1,
        flexDirection: 'row',
        backgroundColor: 'transparent',
        margin: 64,
    },
    button : {
        flex: 1,
        alignSelf: 'flex-end',
        alignItems: 'center',
    },
    preview : {
        alignSelf : 'stretch',
        flex : 1
    },
    message: {
        textAlign: 'center',
        paddingBottom: 10,
    },
    text : {
        fontSize: 24,
        fontWeight: 'bold',
        color: 'white',    
    },
});