import "./PdfViewer.css"

export default function PdfViewer({url, count}){

    return (
        <div class="pdf-container">
            <a class="pdf-link" href={url} target="_blank"> Packet {count}</a>
            <iframe class="pdf-window" src={url} ></iframe>
        </div>
    )
}