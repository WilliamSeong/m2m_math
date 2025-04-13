import { Alert, View, Text, StyleSheet, Pressable, Dimensions, Button } from 'react-native';
import { useEffect, useState } from 'react'
import { useLocalSearchParams, useRouter } from 'expo-router';

import Tab from "./customTab";
import PacketOptions from './PacketModal';

const address = "http://192.168.1.103:9050"

const windowWidth = Dimensions.get('window').width
const windowHeight = Dimensions.get('window').height

interface Student {
    _id : ObjectIdFormat
    name : string
    grade : string
    enrolled : boolean
    join : string
    objectives_complete : Objectives[]
    objectives_inprogress : Objectives[]
    objectives_awaiting : Objectives[]
    packets_inprogress : ObjectIdFormat
    packets_completed : ObjectIdFormat[]
}

interface Packets {
    _id : ObjectIdFormat
    student_id : ObjectIdFormat
    submissions : ObjectIdFormat[]
    date_created : Date
    answer_key : AnswerKey
    content : Content
    submission_details : Submission
}

interface Content {
    $binary : Binary
}

interface Binary {
    base64 : string
    subType : string
}

interface AnswerKey {
    [questionId : string] : string
}

interface Submission {
    [packetId : string] : Array<[Date, Score]>
}

interface Date {
    $date : string
}

interface Score {
    correct : string[]
    incorrect : string[]
}

interface Objectives {
    id : ObjectIdFormat
    name : string
}

interface ObjectIdFormat {
    $oid : string
}

export default function StudentProfile() {

    const {studentId} = useLocalSearchParams();

    const [student, setStudent] = useState<Student>();
    const [packets, setPackets] = useState<Array<[string, string, Array<[Date, Score]>]>>()
    const [modalVisible, setModalVisible] = useState(false);

    
    useEffect(() => {
        const fetchStudentDetails = async () => {
            const response = await fetch(`${address}/student/details`, {
                method : "POST",
                headers : {
                    "Content-Type" : "application/json",
                },
                body : JSON.stringify({
                    studentId : {
                        "$oid" : studentId
                    }
                })
            })

            const data = await response.json();
            
            const parsedData = JSON.parse(data.details)

            // console.log(parsedData.name);

            setStudent(parsedData);
        }

        const fetchStudentPackets = async () => {
            const response = await fetch(`${address}/student/packets`, {
                method : "POST",
                headers : {
                    "Content-Type" : "application/json",
                },
                body : JSON.stringify({
                    studentId : {
                        "$oid" : studentId
                    }
                })
            })

            const data = await response.json();
            
            const parsedData = JSON.parse(data.packets)

            // console.log("Parsed packets", parsedData)

            // Shouldn't I just project this in the query then?
            let urls : Array<[string, string, Array<[Date, Score]>]> = [];
    
            for (const packet of parsedData ) {
                const packetId = packet._id.$oid;
                // console.log("packet Id: ", packetId)

                const pdfDataUrl = `data:application/pdf;base64,${packet.content.$binary.base64}`;
        
                const submissions = packet.submission_details

                // console.log("submissions: ", submissions)

                urls = [...urls, [packetId, pdfDataUrl, submissions]];
            }
            
            // console.log("Urls: ", urls)

            setPackets(urls);
        }

        fetchStudentDetails();
        fetchStudentPackets();
    }, [])

    const router = useRouter();

    const pdfCheck = (id : string) => {
        console.log("pdfCheck: ", id);
        setModalVisible(!modalVisible);
        // router.push({
        //     pathname : "/camera",
        //     params : {id : id}
        // })
    }
    
    const onModalClose = () => {
        setModalVisible(false);
    }

    return(
        <View style={styles.container}>
            {student ? (
                <View style={styles.studentDetailsContainer}>
                    <Text> {student.name} </Text>
                    <Text> Grade: {student.grade} </Text>
                    <Text> Join: {student.join} </Text>

                </View>
                ) : <Text>Loading Details...</Text>
            }
            {packets ? (
                <View style={styles.packetContainer}>
                    {packets.map((packet, index) => (
                        <View key={index}>
                            <Pressable onPress={() => pdfCheck(packet[0])}>
                                <View style={styles.packet}>
                                    <Text style={{fontSize : windowHeight * .04}}>📄 Packet: {packet[0]}</Text>
                                    {/* {(() => {
                                        console.log("Packet uri is: ", packet[1]); 
                                        return null;
                                        })()} */}
                                    {/* <WebView style={styles.webViewContainer} source={{ uri: packet[1]}} /> */}
                                </View>
                            </Pressable>
                        <PacketOptions isVisible={modalVisible} onClose={onModalClose} packetId={packet[0]} submissions={packet[2]} studentId={studentId as string}/>
                        </View>
                    ))}
                </View>
                ) : <Text>Loading Packets...</Text>
            }
            
            <Tab />
        </View>
    )
}

const styles = StyleSheet.create({
    container : {
        height: '100%'
    },
    studentDetailsContainer : {
        borderWidth: 2,
        margin : 5
    },
    packetContainer : {
        width: '100%',
        display: 'flex',
        justifyContent: 'center',
        alignItems : 'center',
    },
    packet : {
        backgroundColor : '#5BC6FC',
        padding : 20,
        width : windowWidth * 0.8,
        height: windowHeight * 0.1,
        borderRadius : 10,
    },
    submissionBad : {
        backgroundColor : '#FC915B',
        width : windowWidth * 0.5,
        height: windowHeight * 0.05,
        borderRadius : 5,
        justifyContent : 'center',
        paddingLeft : 5
    },
    submissionGood : {
        backgroundColor : '#11EE9E',
        width : windowWidth * 0.5,
        height: windowHeight * 0.05,
        borderRadius : 5,
        justifyContent : 'center',
        paddingLeft : 5
    },
    modal : {
        backgroundColor : '#11EE9E'
    }
})