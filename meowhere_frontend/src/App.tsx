//import { useState } from 'react'
import creature from './assets/creature.webp'
import './App.css'
import {Tile} from './components/Tile'
function App() {
  //const [count, setCount] = useState(0)

  return (
    <>
      <h1>Meow</h1>
      <Tile title="Mruczysław" image="https://static.wikia.nocookie.net/silly-cat/images/d/d8/Jinx.png" description="zaginął, bardzo silly"/>
      <img src={creature} alt="Kreatura" />
    </>
  )
}

export default App
