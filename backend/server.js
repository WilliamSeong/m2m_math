import express from 'express';
import cors from 'cors';
import dotenv from "dotenv";
import { MongoClient, ServerApiVersion } from "mongodb";


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

const client = new MongoClient(uri, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  }
});


server.get("/algebra1", algebra1)

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

  const result = await client.db("m2m_math_db").collection("questions").findOne({ level : "algebra 1"});

  if (result) {
    return result;
  } else {
    console.log("no listing");
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

serverStart()
