import { Text, View, StyleSheet, ScrollView, Dimensions, Pressable } from 'react-native';
import { useEffect, useState } from 'react';
import { ObjectId } from 'mongodb';

import { useRouter } from 'expo-router'

const windowWidth = Dimensions.get('window').width
const windowHeight = Dimensions.get('window').height

const address = "http://192.168.1.103:9050"

interface Student {
    _id : ObjectIdFormat
    name : string
    grade : string
    enrolled : true
    objectives_inprogress : Objective[]
    packets_inprogress : ObjectId[]
    last_assignment : Date
    last_submission : Date
}

interface Date {
    $date : string
}

interface Objective {
    id : ObjectIdFormat
    name : string
}

interface ObjectIdFormat {
    $oid: string;
}

export default function index() {

    const router = useRouter();
    const [students, setStudents] = useState<Student[]>()
    const [assignment, setAssignment] = useState<Date>()
    const [submission, setSubmission] = useState<Date>()

    useEffect(() => {

        async function fetchData() {

            const response = await fetch(`${address}/student/all`);

            const data = await response.json();

            console.log(data)

            console.log("last_submission Data: ", data[0].last_submission.$date);

            setStudents(data);
        };

        fetchData();
    }, []);

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
        
        return `${month} ${day}, ${year}`;
    }

    return(
        <View style={styles.container}>
            {students ? (
                <ScrollView style={styles.scroll}>
                        {students.map((student, index) => (
                            <Pressable 
                                key={index} 
                                style={styles.card}
                                onPress={() => router.push({
                                    pathname : "../components/studentProfile",
                                    params : { studentId: student._id.$oid }
                                })}
                                >
                                <Text style={styles.studentName}>{student.name}</Text>
                                <Text>{student._id.$oid}</Text>
                                <View style={styles.cardContent}>
                                    <Text style={styles.studentFields}>Grade: {student.grade}</Text>
                                    <Text style={styles.studentFields}>Packets in progress: {student.packets_inprogress.length}</Text>
                                    <Text style={styles.studentFields}>Last Assignment: {formatDate(student.last_assignment.$date)}</Text>
                                    <Text style={styles.studentFields}>Last Submission: {formatDate(student.last_submission.$date)}</Text>
                                </View>
                            </Pressable>
                        ))}
                </ScrollView>
            ) : <View>
                    <Text>Loading...</Text>
                </View>}
        </View>
    )
}

const styles = StyleSheet.create({
    container : {
        flex : 1
    },
    scroll : {
        height: '100%'
    },
    card : {
        backgroundColor : '#5BC6FC',
        margin : 10,
        height: windowHeight * .2,
        borderRadius : 32,
        padding : 10
    },
    cardContent : {
        backgroundColor : 'white',
        height : windowHeight * .11,
        borderRadius : 10,
        padding : 5,
        margin : 5,
    },
    studentName : {
        fontSize : 40,
    },
    studentFields : {
        fontSize : 20,
    }
})