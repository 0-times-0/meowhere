export function Tile({title, image, description}: any){
    return <>
        <h1>{title}</h1>
        <img src={image}></img>
        <p>{description}</p>
    </>
}