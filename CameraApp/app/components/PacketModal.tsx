import { Modal, View, Text, Pressable, StyleSheet, ScrollView } from 'react-native';
import { PropsWithChildren } from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useRouter } from 'expo-router'

interface Date {
    $date : string
}

interface Score {
    correct : string[]
    incorrect : string[]
}

type Props = PropsWithChildren<{
    isVisible : boolean;
    onClose : () => void;
    packetId : string;
    submissions : Array<[Date, Score]>
    studentId : string
}>;

export default function PakcetModal({isVisible, onClose, packetId, submissions, studentId} : Props) {
    
    function formatDate(isoString : string) {
        const date = new Date(isoString);
        
        // Force UTC time interpretation
        const month = date.toLocaleString('en-US', { month: 'long', timeZone: 'UTC' });
        const day = date.getUTCDate();
        const year = date.getUTCFullYear();
        
        // Get time components
        const hours = date.getUTCHours();
        const minutes = date.getUTCMinutes();
        const period = hours >= 12 ? 'PM' : 'AM';

        // Convert to 12-hour format
        const formattedHours = hours % 12 || 12;
        
        // Format time with leading zeros for minutes
        const formattedMinutes = minutes.toString().padStart(2, '0');
        
        return `${month} ${day}, ${year} (${formattedHours}:${formattedMinutes} ${period})`;
    }

        const router = useRouter();
    
        const pdfCheck = () => {
            console.log("pdfCheck: ", packetId, " for ", studentId);
            onClose();
            router.push({
                pathname : "/camera",
                params : {
                            id : packetId,
                            studentId : studentId
                        }
            })
        }
    
    
    return(
        <View>
            <Modal animationType="fade" transparent={true} visible={isVisible}>
                <Pressable style={styles.nonModalContent} onPress={onClose} />

                <View style={styles.modalContent}>
                    <View style={styles.titleContainer}>
                            <Text>{packetId}</Text>
                            <Pressable onPress={onClose}>
                                <FontAwesome name="close" color="#fff" size={25} />
                            </Pressable>
                    </View>
                    <View style={styles.modalOptions}>
                        <View style={styles.modalOptionSubmissions}>
                            <ScrollView>
                                {submissions.slice().reverse().map((submission, index)=> (
                                    <View key={index} 
                                        style={submission[1].correct.length/(submission[1].incorrect.length + submission[1].correct.length) > .95 ? 
                                        styles.submissionGood : 
                                        styles.submissionBad
                                        }>
                                        <Text>{formatDate(submission[0].$date)} : {submission[1].correct.length}/{submission[1].incorrect.length + submission[1].correct.length} </Text>
                                        <Text>{submission[1].incorrect.length === 0 ? 'Good Job!' : `Incorrect: [${submission[1].incorrect.join(', ')}]`}</Text>
                                    </View>
                                ))}
                            </ScrollView>
                        </View>
                        <View style={styles.modalOptionCamera}>
                            <Pressable style={styles.modalOptionCameraButton} onPress={pdfCheck}>
                                <FontAwesome name="camera" color="#fff" size={25} />
                            </Pressable>
                        </View>
                    </View>
                </View>
            </Modal>
        </View>
    )
}

const styles = StyleSheet.create({
    nonModalContent : {
        backgroundColor : 'rgba(0,0,0,0.5)',
        height : '80%',
        width : '100%'
    },
    modalContent : {
        height: '20%',
        width: '100%',
        backgroundColor: '#5BC6FC',
        position: 'absolute',
        bottom: 0,
        justifyContent : 'flex-end',
    },
    titleContainer : {
        height: '20%',
        backgroundColor: '#5BC6FC',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'flex-end',
    },
    modalOptions : {
        flexDirection : 'row',
        height : '100%',
    },
    modalOptionSubmissions : {
        width : '60%',
        borderWidth : 2,
    },
    modalOptionCamera : {
        width : '40%',
        // borderWidth : 2,
        justifyContent : 'center',
        alignItems : 'center'
    },
    modalOptionCameraButton : {
        borderWidth : 2,
        borderRadius : 50,
        padding : 20,
        backgroundColor : 'rgba(255,255,255,0.3)'
    },
    submissionBad : {
        backgroundColor : '#FC915B',
        justifyContent : 'center',
        paddingLeft : 5
    },
    submissionGood : {
        backgroundColor : '#11EE9E',
        justifyContent : 'center',
        paddingLeft : 5
    },

})