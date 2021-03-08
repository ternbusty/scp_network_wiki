from modules_jp import SCP, MarkdownWriter, GraphDataWriter

if __name__ == '__main__':
    scp = SCP('../../yaml/jp/')

    path = '../../'
    mdw = MarkdownWriter(scp, path)
    mdw.save_to_markdown()

    gdw = GraphDataWriter(scp, '../../graph/jp/')
    gdw.save_to_csv()
