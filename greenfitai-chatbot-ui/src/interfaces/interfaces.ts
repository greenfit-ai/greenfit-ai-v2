export interface message{
    content:string;
    role:string;
    id:string;
}

export interface Message {
    content: {
      text: string;
      chartData?: number[];
    };
    role: "user" | "assistant";
    id: string;
}
