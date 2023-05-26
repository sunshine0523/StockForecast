export class AskInput {
    key: string
    value: string
}
export class Ask {
    value: string
    inputs: AskInput[]

    constructor(value: string) {
        this.value = value
        this.inputs = new AskInput()[0];
    }
}