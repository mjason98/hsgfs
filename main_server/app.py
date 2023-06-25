from flask import Flask, make_response, jsonify, request
from services.connect import create_conn, SCHEMA
from services.chuncks import get_distro_chunks
from services.chuncks import gen_chunks_handlers
import requests, sys


app = Flask(__name__)
CHUNK_SIZE = 1024  # 1Kb


@app.route('/get_chunk_distro/<filename>')
def get_chunk_distro(filename):
    try:
        conn = create_conn()

        query = f'''
            select id from {SCHEMA}.files where filename='{filename}'
        '''

        conn.execute(query)
        fileid = conn.fetchone()

        assert fileid is not None,\
            f'File {filename} does not exist'

        fileid = fileid[0]

        query = f'''select t1.chunk_handler, t2.server_name
                    from {SCHEMA}.chunks as t1
                    left join {SCHEMA}.chunks_map as t2
                        on t1.chunk_handler = t2.chunk_handler
                    where fileid={fileid}
                    order by t1.chunk_pos
        '''

        conn.execute(query)
        echunks = conn.fetchall()

        result_handlers = [ec[0] for ec in echunks]
        result_servers = [ec[1] for ec in echunks]

        return make_response(jsonify({
            'handlers': result_handlers,
            'servers': result_servers,
            'fileid': fileid}),
            200)

    except Exception as ex:
        print(f"An error apear {str(ex)}", file=sys.stderr)
        return make_response(jsonify({'message': str(ex)}), 400)


@app.route('/gen_chunk_distro', methods=['POST'])
def gen_chunk_distro():
    try:
        request_body = request.get_json()
        conn = create_conn()

        result_handlers = []
        result_servers = []

        assert 'filesize' in request_body,\
            "The request body does not have filesize"

        assert 'filename' in request_body,\
            "The request body does not have a filename"

        filesize = int(request_body['filesize'])
        filename = request_body['filename']

        total_chunks = int((filesize + CHUNK_SIZE - 1) / CHUNK_SIZE)
        existing_chunks = 0

        query = f'''
            select id from {SCHEMA}.files where filename='{filename}'
        '''

        conn.execute(query)
        fileid = conn.fetchone()

        if fileid is not None:
            fileid = fileid[0]

            query = f'''select t1.chunk_handler, t1.chunk_pos, t2.server_name
                        from {SCHEMA}.chunks as t1
                        left join {SCHEMA}.chunks_map as t2
                            on t1.chunk_handler = t2.chunk_handler
                        where fileid={fileid}
                        order by chunk_pos
            '''

            conn.execute(query)
            echunks = conn.fetchall()

            existing_chunks = len(echunks) if echunks is not None else 0

            result_servers += [ec[2] for ec in echunks]
            result_handlers += [ec[0] for ec in echunks]
        else:
            query = f'''insert into {SCHEMA}.files (filename, chunks, filesize)
                values ('{filename}', {total_chunks}, {filesize})
                returning id
            '''

            conn.execute(query)
            fileid = conn.fetchone()[0]

        remaning_chunks = total_chunks - existing_chunks

        if remaning_chunks < 0:
            # delete old chunks
            query_d = f'''
                delete from {SCHEMA}.chunks where
                fileid={fileid} and chunk_pos>={total_chunks}
            '''

            conn.execute(query_d)

            result_servers = result_servers[:total_chunks]
            result_handlers = result_handlers[:total_chunks]

        elif remaning_chunks > 0:
            new_chunks_servers = get_distro_chunks(remaning_chunks)
            result_servers += new_chunks_servers

            new_handlers = gen_chunks_handlers(
                    filename,
                    existing_chunks,
                    total_chunks)

            result_handlers += new_handlers

            for chs, chh, chp in zip(new_chunks_servers,
                                     new_handlers,
                                     range(existing_chunks, total_chunks)):

                query_c = f''' insert into
                    {SCHEMA}.chunks (chunk_handler, fileid, chunk_pos)
                    values ('{chh}', {fileid}, {chp})
                '''

                query_s = f'''insert into
                    {SCHEMA}.chunks_map (chunk_handler, server_name)
                    values ('{chh}', '{chs}')
                '''

                conn.execute(query_c)
                conn.execute(query_s)

        conn.execute('commit')

        return make_response(jsonify({
            'handlers': result_handlers,
            'servers': result_servers,
            'fileid': fileid}),
            200)

    except Exception as ex:
        print(f'An error apear {str(ex)}', file=sys.stderr)
        return make_response(jsonify({
            'message': str(ex)}),
            400)


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_by_filename(filename):
    try:
        conn = create_conn()

        query = f'''
            select id from {SCHEMA}.files where filename='{filename}'
        '''

        conn.execute(query)
        fileid = conn.fetchone()

        assert fileid is not None, f'File {filename} not exist'

        fileid = fileid[0]

        query = f'''select t1.chunk_handler, t2.server_name
                    from {SCHEMA}.chunks as t1
                    left join {SCHEMA}.chunks_map as t2
                        on t1.chunk_handler = t2.chunk_handler
                    where t1.fileid={fileid}
                    order by t1.chunk_pos
        '''

        conn.execute(query)
        echunks = conn.fetchall()

        print(f'Attempt to delete chunks from file {filename}', file=sys.stderr)
        for chh, chs in echunks:
            try:
                del_url = f'{chs}/delete_chunk/{chh}'
                response = requests.delete(del_url)

                msg = response.json()['message']

                assert response.status_code == 200, msg
            except Exception as ex:
                print(f'> Error {str(ex)}', file=sys.stderr)
                print(f'> Skiped chunk {chh} in {chs}', file=sys.stderr)

        query = f'''delete from {SCHEMA}.files
            where id={fileid}
        '''

        conn.execute(query)
        conn.execute('commit')

        return make_response(jsonify({'message': 'deleted file'}), 200)

    except Exception as ex:
        print(f"An error apear {str(ex)}", file=sys.stderr)
        return make_response(jsonify({'message': str(ex)}), 400)


@app.route('/getsize/<filename>', methods=['GET'])
def get_file_size(filename):
    try:
        conn = create_conn()
        query = f'''select id, filesize from
                {SCHEMA}.files
                where filename='{filename}'
        '''

        conn.execute(query)
        result = conn.fetchone()

        assert result is not None,\
            f'File {filename} may not exist'

        return make_response(jsonify({
            'filename': filename,
            'fileid': result[0],
            'filesize': result[1]}),
            200)
    except Exception as ex:
        print(f'Error {str(ex)}', file=sys.stderr)
        return make_response(jsonify({
            'status': 400,
            'message': str(ex)}),
            400)


if __name__ == '__main__':
    app.run(port=8020)
