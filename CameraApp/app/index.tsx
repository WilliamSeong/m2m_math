import { Text, View, StyleSheet, Button, TouchableOpacity, Pressable, TextInput } from "react-native";
import { Image } from 'expo-image';
import { CameraView, CameraType, useCameraPermissions } from 'expo-camera';
import { useRef, useState } from 'react';

import * as FileSystem from 'expo-file-system';
import * as ImageManipulator from 'expo-image-manipulator';

export default function Index() {
    let cameraRef = useRef<CameraView>(null);

    const [facing, setFacing] = useState<CameraType>('back');
    const [cameraPermission, requestCameraPermission] = useCameraPermissions();
    const [photo, setPhoto] = useState<string | undefined>();
    const [packetId, setPacketId] = useState("");

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

        if (!newPhoto) return;

        const manipulatedPhoto = await ImageManipulator.manipulateAsync(
            newPhoto.uri,
            [{ resize: { width: 2000, height: 2000 } }],
            { format: ImageManipulator.SaveFormat.JPEG, compress: 0.8 }
        );
    

        let imageData;
    
        if (manipulatedPhoto?.uri.startsWith('file://')) {
            // It's a file reference - convert to the actual base64 image
            const base64 = await FileSystem.readAsStringAsync(manipulatedPhoto.uri, { encoding: FileSystem.EncodingType.Base64 });
            imageData = `data:image/jpeg;base64,${base64}`;
        } else {
            // It's already a data URI
            imageData = manipulatedPhoto?.uri;
        }
        
        setPhoto(imageData);
    }

    const pushToMongo = async () => {
        try{
            // console.log("Image uri: ", photo);
            const response = await fetch("http://192.168.1.8:9050/camera", {
                method : "POST",
                headers : {
                    "Content-Type" : "application/json",
                },
                body : JSON.stringify({
                    uri : photo
                })
            });
        } catch(e) {
            console.log("Fetch error: ", e);
        }
    };


    const process = async () => {
        try{
            const response = await fetch("http://192.168.1.8:9050/process", {
                method : "POST",
                headers : {
                    "Content-Type" : "application/json",
                },
                body : JSON.stringify({
                    uri : photo,
                    packetId : packetId
                })
            });
        } catch(e) {
            console.log("Process error: ", e);
        }
    }

    const renderImage = () => {
        return(
            <View>
                <TextInput
                    style={styles.input}
                    onChangeText={setPacketId}
                    value={packetId}
                    placeholder="Packet Id"
                />

                <Image
                    source={ photo }
                    contentFit="contain"
                    style={{ width: 300, aspectRatio: 1 }}
                />
                <Button onPress={() => setPhoto(undefined)} title="Take another picture" />
                <Button onPress={pushToMongo} title="Send to Mongo" />
                <Button onPress={process} title="Process" />
            </View>
        );
    };

    const testServer = async() => {
        try{
            const response = await fetch("http://192.168.1.103:9050/test");
            const data = await response.json();
            console.log(data);
        } catch(e) {
            console.log("Flask server request error: ", e);
        }
    }

    const renderCamera = () => {
        return(
            <CameraView style={styles.camera} facing={facing} ref={cameraRef} flash="on">
                <View style={styles.buttonContainer}>
                    <TouchableOpacity style={styles.button} onPress={toggleCameraFacing}>
                        <Text style={styles.text}>Flip Camera</Text>
                    </TouchableOpacity>
                </View>
                <Pressable onPress={takePic} style={{
                    backgroundColor: 'white',
                    paddingVertical: 12,
                    paddingHorizontal: 30,
                    borderRadius: 30,
                    bottom : 50,
                    width : "25%",
                    margin : 'auto'
                }}>
                    <Text>PIC</Text>
                </Pressable>
                <Pressable onPress={testServer} style={{
                    backgroundColor: 'white',
                    paddingVertical: 12,
                    paddingHorizontal: 30,
                    borderRadius: 30,
                    bottom : 50,
                    width : "25%",
                    margin : 'auto'
                }}><Text>Test Server</Text></Pressable>
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
    input: {
        height: 40,
        margin: 12,
        borderWidth: 1,
        padding: 10,
      },
});