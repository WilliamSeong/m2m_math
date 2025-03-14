import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { MongoClient, ServerApiVersion, ObjectId } from "mongodb";
import PDFDocument from "pdfkit";

const server = express();
const port = 3000;
server.use(express.json());


server.use(cors({
    origin: 'http://localhost:5173',
}));


server.get("/test", (req, res) => {
    res.send({"message" : "hello from server"});
});

dotenv.config();

const mongoUser = process.env.MONGODB_USER;
const mongoPassword = process.env.MONGODB_PASSWORD;
const uri = `mongodb+srv://${mongoUser}:${mongoPassword}@young-by-nail.vhysf.mongodb.net/?retryWrites=true&w=majority&appName=young-by-nail`;

console.log(uri);

const client = new MongoClient(uri, {
    serverApi: {
        version: ServerApiVersion.v1,
        strict: true,
        deprecationErrors: true,
    }
});


server.get("/algebra1", algebra1)
server.get("/all", all)
server.get("/random5", random5);
server.get("/students", students);
server.post("/student/details", studentDetails);
server.post("/generate", generateQuestions);
server.get("/pdf", testPDF);

// Fetch one question
async function algebra1(req, res) {
    console.log("Fetching algebra 1");

    try{
        const result = await fetchAlgebra1(client);
        console.log(result);
        res.json(result);
    } catch(e) {
        console.log("Algebra fetch error: ", e);
    }
}

async function fetchAlgebra1(client) {

    const result = await client.db("m2m_math_db").collection("questions").findOne();

    if (result) {
        return result;
    } else {
        console.log("no listing");
    }
}

// Fetch all questions
async function all(req, res) {
    console.log("Fetching algebra 1");

    try{
        const result = await fetchAll(client);
        console.log(result);
        res.json(result);
    } catch(e) {
        console.log("Algebra fetch error: ", e);
    }
}

async function fetchAll(client) {
    const cursor = await client.db("m2m_math_db").collection("questions").find();
    const result = await cursor.toArray();

    if (result != 0) {
        return result;
    } else {
        console.log("no listings");
    }
}

// Fetch all students
async function students(req, res) {
    console.log("Fetching student");
    try {
        const result = await fetchStudents(client);

        res.json(result);
    } catch(e) {
        console.log("Student fetching error: ", e);
    }
}

async function fetchStudents(client) {
    const cursor = await client.db("m2m_math_db").collection("students").find();
    const result = cursor.toArray();

    return result;
}

// Fetch details of one student using studentId
async function studentDetails(req, res) {
    console.log("Fetching student details");
    const { studentId } = req.body;
    try {
        const result = await fetchStudentDetails(client, studentId);

        const packets = await fetchStudentPackets(client, studentId);

        // console.log("This student's packets: ", packets);

        res.json({result : result, packets : packets});
    } catch(e) {
        console.log("Student details fetching error: ", e);
    }
}

async function fetchStudentDetails(client, studentId) {
    const result = await client.db("m2m_math_db").collection("students").findOne({_id : ObjectId.createFromHexString(studentId)});
    return result;
}

async function fetchStudentPackets(client, student) {

    console.log("Checking packets for student id: ", student);

    const cursor = await client.db("m2m_math_db").collection("packets").find({student_id : ObjectId.createFromHexString(student)});
    const packets = await cursor.toArray();

    return packets;
}

// Generate questions using a list of objectives (5 each, for now)

async function generateQuestions(req, res) {
    const { objectiveList, studentId } = req.body;

    console.log(objectiveList, studentId);

    try {
        const result = await generateRandomQuestions(client, objectiveList);

        // console.log("these are the generated questions", result);

        const doc = new PDFDocument();

        const buffer = [];

        doc.on("data", buffer.push.bind(buffer));
        doc.on("end", async () => {
            const pdfData = Buffer.concat(buffer);

            await createPacket(client, pdfData, studentId);

            res.setHeader("Content-Type", "application/pdf");
            res.setHeader("Content-Disposition", "inline; filename=output.pdf");
            res.end(pdfData);
        })

        for (const question of result) {
            doc.text(question.question);
        }
        doc.end();

    } catch(e) {
        console.log("Generate error :", e);
    }
}

async function createPacket(client, packet, student) {
    console.log("Creating packet");
    const response = await client.db("m2m_math_db").collection("packets").insertOne({ content : packet, student_id : ObjectId.createFromHexString(student), date_created : new Date()});
    const packetId = response.insertedId;
    await client.db("m2m_math_db").collection("students").updateOne({ _id : ObjectId.createFromHexString(student)}, {$push : {packets_inprogress : packetId}});
}

async function generateRandomQuestions(client, objectives) {
    let generatedQuestions = [];
    for (const obj of objectives) {
        generatedQuestions = [...generatedQuestions, ...await fetchRandomFive(client, obj)]
    }

    return generatedQuestions;
}

// Fetch 5 random questions from an objective
async function random5(req, res) {
    try {
        const result = await fetchRandomFive(client, "multiply integers");
        console.log(result);
        res.json(result);
    } catch(e) {
        console.log("Error: ", e);
    }
}

async function fetchRandomFive(client, objective) {
    const result = await client.db("m2m_math_db").collection("objectives").findOne({_id : ObjectId.createFromHexString(objective)});
    // const result = await cursor.toArray();
    let randomFive = [];
    if (result.questions && result.questions) {
        // Shuffle array and take first n elements
        const shuffled = result.questions.sort(() => 0.5 - Math.random());
        randomFive = shuffled.slice(0, 5);
    }
    // console.log(randomFive);

    const cursor = await client.db("m2m_math_db").collection("questions").find({_id : {$in: randomFive}})
    const result2 = await cursor.toArray();

    // console.log(result2);
    return result2;
}

async function testPDF(req, res) {

    // Set response headers
    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", "inline; filename=output.pdf");

    const doc = new PDFDocument();
    doc.pipe(res);
    doc.text("Hello, World!");
    doc.end();
}


// Sort questions into objective's questions array
async function sort(client) {
    const cursor = await client.db("m2m_math_db").collection("questions").find();
    const result = await cursor.toArray();

    for (const question of result){
        console.log("id: ",question._id);
        console.log("objective: ",question.objective_id);

        const response = await client.db("m2m_math_db").collection("objectives").updateOne({_id : question.objective_id}, { $addToSet: {questions : question._id}})
    }
}

async function serverStart() {
    try{
        await client.connect()
        console.log('MongoDB connected')

        server.listen(port);
        console.log(`Express Server is listening at http://localhost:${port}`);
    }catch(e){
        console.log("Server Start Error:", e);
    }
}

serverStart();
// sort(client);
// fetchRandomFive(client, "multiply integers");