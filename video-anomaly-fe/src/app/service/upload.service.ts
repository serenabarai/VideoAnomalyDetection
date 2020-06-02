import { Injectable } from '@angular/core';
import { FileUploader } from 'ng2-file-upload';
import { HttpClientModule, HttpHeaders, HttpClient } from '@angular/common/http';
import { stringify } from 'querystring';
import { timeout, retry, retryWhen, delayWhen, mergeMap, finalize, catchError } from 'rxjs/operators';
import { timer, Observable, throwError, of } from 'rxjs';

const httpOptions = {
  responseType: 'arraybuffer' as 'json',
  headers: new HttpHeaders({ 'Cache-Control':'no-cache','Content-Type': 'video/mp4' })
};

const httpOptionsJson = {
  headers: new HttpHeaders({  'Cache-Control':'no-cache', 'Content-Type': 'application/json' })
};

const genericRetryStrategy = ({
  maxRetryAttempts = 3,
  scalingDuration = 1000,
  excludedStatusCodes = []
}: {
  maxRetryAttempts?: number,
  scalingDuration?: number,
  excludedStatusCodes?: number[]
} = {}) => (attempts: Observable<any>) => {
  return attempts.pipe(
    mergeMap((error, i) => {
      const retryAttempt = i + 1;
      // if maximum number of retries have been met
      // or response is a status code we don't wish to retry, throw error
      if (
        retryAttempt > maxRetryAttempts ||
        excludedStatusCodes.find(e => e === error.status)
      ) {
        return throwError(error);
      }
      // console.log(
      //   `Attempt ${retryAttempt}: retrying in ${retryAttempt *
      //     scalingDuration}ms`
      // );

      console.log(
        `Attempt ${retryAttempt}: retrying in 2 mins`
      );

      // retry after 1s, 2s, etc...
      //return timer(retryAttempt * scalingDuration);

      //retry every 2 mins
      return timer(120000)
    }),
    finalize(() => console.log('We are done!'))
  );
};



@Injectable({
  providedIn: 'root'
})
export class UploadService {

  public uploader: FileUploader

  constructor(private http:HttpClient) { 
    this.uploader = new FileUploader({ url: '/api/upload', itemAlias: 'file' });
    this.uploader.onAfterAddingFile = (file) => {file.withCredentials = false}
    this.uploader.onCompleteItem = (item:any, response: any, status: any, header:any) => {
      console.log('File uploaded')
    }
  }

  getProcessedVideo(){
    console.log('making get request for video')
    return this.http.get<any>('/api/processed_video', httpOptions)
                    .pipe(
                      retryWhen(genericRetryStrategy({
                        maxRetryAttempts: 10,
                        scalingDuration: 2000,
                        excludedStatusCodes: [500,504]
                      })),
                      catchError(err => of(err))
                    )
  }

  getVideoAnnotations(){
    console.log('making get request for video annotations')
    return this.http.get<any>('/api/annotations', httpOptionsJson)
                    .pipe(
                      retryWhen(genericRetryStrategy({
                        maxRetryAttempts: 10,
                        scalingDuration: 2000,
                        excludedStatusCodes: [500,504]
                      })),
                      catchError(err => of(err))
                    )
  }

}
