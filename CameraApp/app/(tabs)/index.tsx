import { Text, View, StyleSheet } from 'react-native';
import { useEffect, useState } from 'react';
import { ObjectId } from 'mongodb';

const address = "http://192.168.1.103:9050"

interface Student {
    _id : ObjectIdFormat
    name : string
    enrolled : true
    objectives_inprogress : Objective[]
    packets_inprogress : ObjectId[]
}

interface Objective {
    id : ObjectIdFormat
    name : string
}

interface ObjectIdFormat {
    $oid: string;
}

export default function index() {

    const [students, setStudents] = useState<Student[]>()

    useEffect(() => {

        async function fetchData() {

            const response = await fetch(`${address}/student/all`);

            const data = await response.json();

            console.log(data);

            setStudents(data);
        };

    fetchData();

    }, []);


    return(
        <View>
            {students ? (
                <View>
                    {students.map((student, index) => (
                        <Text key={index}>{student.name}</Text>
                    ))}
                </View>
            ) : <View>
                    <Text>Loading...</Text>
                </View>}
        </View>
    )
}

