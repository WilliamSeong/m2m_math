import "./PdfViewer.css"

export default function PdfViewer({url, count}){

    return (
        <div className="pdf-container">
            <a className="pdf-link" href={url} target="_blank"> Packet {count + 1}</a>
            <iframe className="pdf-window" src={url} ></iframe>
        </div>
    )
}