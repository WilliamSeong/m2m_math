import "./PdfViewer.css"

const address = "http://192.168.1.103:9050"

export default function PdfViewer({studentId, packetId, url, count}){

    async function completePacket() {
        console.log("Completing: ", packetId, " for student ", studentId);
        if (window.confirm(`Remove packet ${packetId}`)) {
            try{
                const response = await fetch(`${address}/student/packet/remove`, {
                    method : "POST",
                    headers : {
                        "Content-Type" : "application/json",
                    },
                    body : JSON.stringify({
                        packetId : packetId,
                        studentId :studentId
                    })
                });

            } catch(e) {
                console.log("Packet removing error", e)
            }
        }
    }

    return (
        <div className="pdf-container">
            <a className="pdf-link" href={url} target="_blank"> Packet {count + 1}</a>
            <div className="mark-complete" onClick={completePacket}>Mark Complete</div>
            <iframe className="pdf-window" src={url} ></iframe>
        </div>
    )
}