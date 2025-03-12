import express from 'express';
import cors from 'cors';

const server = express();
const port = 3000;
server.use(express.json());

server.use(cors({
    origin: 'http://localhost:5173',
  }));

server.listen(port);
console.log(`Express Server is listening at http://localhost:${port}`);

server.get("/test", (req, res) => {
    res.send({"message" : "hello from server"});
});