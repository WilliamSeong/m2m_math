import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { MongoClient, ServerApiVersion } from "mongodb";
import { PDFDocument } from "pdfkit";

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

async function random5(req, res) {
    try {
        const result = await fetchRandomFive(client, "multiply integers");
        console.log(result);
        res.json(result);
    } catch(e) {
        console.log("Error: ", e);
    }
}

async function students() {
    const result = await client.db("m2m_math_db").collection("students").find()
}

async function fetchRandomFive(client, objective) {
    const result = await client.db("m2m_math_db").collection("objectives").findOne({name : objective});
    // const result = await cursor.toArray();
    let randomFive = [];
    if (result.questions && result.questions) {
        // Shuffle array and take first n elements
        const shuffled = result.questions.sort(() => 0.5 - Math.random());
        randomFive = shuffled.slice(0, 5);
    }
    console.log(randomFive);

    const cursor = await client.db("m2m_math_db").collection("questions").find({_id : {$in: randomFive}})
    const result2 = await cursor.toArray();

    console.log(result2);
    return result2;
}

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