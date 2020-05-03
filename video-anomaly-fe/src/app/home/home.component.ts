import { Component, ElementRef, ViewChild, Renderer2} from '@angular/core';
import { UploadService } from '../service/upload.service';
import { timeout, retry } from 'rxjs/operators';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent{
  @ViewChild('videoElm') videoElm: ElementRef


  constructor(public uploadService: UploadService, private renderer: Renderer2) {   }

  uploadFile(){
    this.uploadService.uploader.uploadAll()
  }
  getProcessedVideo(){
    this.uploadService.getProcessedVideo().subscribe(data=>{
      console.log('received processed video from server', data)
      const fileType = "video/mp4"
      //const blob = new Blob(data , {type: fileType });
      const blob = new Blob([data])
      const src = URL.createObjectURL(blob);
      //this.videoElm.src = src;
      const elementInsert = this.renderer.createElement('source')
      elementInsert.src = src
      elementInsert.type = 'video/mp4'
      this.renderer.appendChild(this.videoElm.nativeElement, elementInsert)
      this.videoElm.nativeElement.play()

    }, error => {
      console.log(error)
    })
  }
}
